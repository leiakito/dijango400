"""
Game services - 排行榜抓取与同步
"""
import logging
import re
from datetime import date
from typing import List, Optional

import requests
from django.db import transaction
from django.utils import timezone
from parsel import Selector

from .models import SinglePlayerRanking, Game, Publisher, Tag

logger = logging.getLogger(__name__)

# 伪装为常见浏览器的请求头
DEFAULT_HEADERS = {
    'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/120.0.0.0 Safari/537.36'),
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'Referer': 'https://www.3dmgame.com/',
    'Upgrade-Insecure-Requests': '1',
}

RANKING_URL = 'https://www.3dmgame.com/phb.html'


def _parse_release_date(raw: str) -> Optional[date]:
    """解析日期文本（支持 2011年11月11日 / 2011-11-11 形式）"""
    if not raw:
        return None
    cleaned = raw.strip()
    match = re.search(r'(\d{4})[年./-](\d{1,2})[月./-](\d{1,2})', cleaned)
    if not match:
        return None
    try:
        return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
    except ValueError:
        return None


def _safe_int(raw: Optional[str]) -> int:
    """提取数字"""
    if not raw:
        return 0
    digits = re.findall(r'\d+', raw)
    return int(digits[0]) if digits else 0


def _match_game(name: str) -> Optional[Game]:
    """尝试用名称在本地游戏表中找到匹配的游戏"""
    try:
        exact = Game.objects.filter(name__iexact=name).first()
        if exact:
            return exact
        return Game.objects.filter(name__icontains=name).order_by('-heat_total').first()
    except Exception as exc:  # noqa: broad-except
        logger.warning("匹配游戏失败 %s: %s", name, exc)
        return None


def _fetch_3dm_html() -> str:
    """请求 3DM 排行榜页面"""
    response = requests.get(
        RANKING_URL,
        headers=DEFAULT_HEADERS,
        timeout=15,
    )
    response.raise_for_status()
    return response.text


def _parse_3dm_items(html: str) -> List[dict]:
    """从 HTML 中提取排行榜条目"""
    selector = Selector(text=html)
    items = []

    for idx, node in enumerate(selector.css('.Phbright .phlist'), start=1):
        name = (node.css('.bt a::text').get() or '').strip()
        english_name = (node.css('.bt span::text').get() or '').strip()
        detail_url = node.css('.bt a::attr(href)').get() or ''
        cover_url = (
            node.css('a.img img::attr(data-original)').get()
            or node.css('a.img img::attr(src)').get()
            or ''
        )

        info_texts = [t.strip() for t in node.css('.infolis li::text').getall() if t.strip()]
        info_map = {text.split('：', 1)[0]: text.split('：', 1)[1].strip() for text in info_texts if '：' in text}

        tags = [t.strip() for t in node.css('.infolis li a::text').getall() if t.strip()]
        score_text = (node.css('.score_a span::text').get() or '').strip()
        rank_text = (node.css('.scobox .num::text').get() or '').strip()
        rating_text = (node.css('.score_a p::text').get() or '').strip()

        items.append({
            'rank': int(rank_text or idx),
            'name': name,
            'english_name': english_name,
            'developer': info_map.get('开发', ''),
            'publisher_name': info_map.get('发行', ''),
            'release_date': _parse_release_date(info_map.get('发售', '')),
            'genre': info_map.get('类型', ''),
            'platforms': info_map.get('平台', ''),
            'language': info_map.get('语言', ''),
            'score': float(score_text) if score_text.replace('.', '', 1).isdigit() else None,
            'rating_count': _safe_int(rating_text),
            'tags': tags,
            'cover_url': cover_url,
            'detail_url': detail_url
        })

    return items


def sync_3dm_single_player_ranking() -> int:
    """
    抓取并同步 3DM 单机排行榜
    :return: 更新的条目数量
    """
    logger.info("开始同步 3DM 单机排行榜")
    html = _fetch_3dm_html()
    items = _parse_3dm_items(html)
    fetched_at = timezone.now()
    ranks = [item['rank'] for item in items]

    with transaction.atomic():
        for item in items:
            matched_game = _match_game(item['name'])
            SinglePlayerRanking.objects.update_or_create(
                source='3dm',
                rank=item['rank'],
                defaults={
                    'name': item['name'],
                    'english_name': item['english_name'],
                    'developer': item['developer'],
                    'publisher_name': item['publisher_name'],
                    'genre': item['genre'],
                    'platforms': item['platforms'],
                    'language': item['language'],
                    'release_date': item['release_date'],
                    'score': item['score'],
                    'rating_count': item['rating_count'],
                    'tags': item['tags'],
                    'cover_url': item['cover_url'],
                    'detail_url': item['detail_url'],
                    'game': matched_game,
                    'fetched_at': fetched_at,
                }
            )

        # 清理当前来源中已不存在的排名
        SinglePlayerRanking.objects.filter(source='3dm').exclude(rank__in=ranks).delete()

    logger.info("3DM 单机排行榜同步完成，共 %s 条", len(items))
    return len(items)


def _simulate_metric(rank: int, base: int = 50000, step: int = 1200) -> int:
    """根据排名生成一个递减的模拟数值"""
    val = max(0, base - (rank - 1) * step)
    return val


def sync_rankings_to_games(source: str = '3dm') -> int:
    """
    将排行榜数据同步/写入 Game 列表，用抓取到的信息填充分类、评分、热度等。
    返回创建或更新的条目数。
    """
    rankings = list(SinglePlayerRanking.objects.filter(source=source).order_by('rank'))
    if not rankings:
        return 0

    synced = 0
    default_category = '单机'
    default_publisher_name = '未知发行商'

    for item in rankings:
        publisher_name = item.publisher_name or default_publisher_name
        publisher, _ = Publisher.objects.get_or_create(
            name=publisher_name,
            defaults={'description': '自动导入（3DM 排行榜）'}
        )

        category = item.genre or default_category
        score_val = float(item.score) if item.score is not None else None
        rating = score_val if score_val is not None else max(0, 9.5 - item.rank * 0.05)
        download_count = _simulate_metric(item.rank, base=300000, step=8000)
        follow_count = _simulate_metric(item.rank, base=80000, step=2000)
        review_count = item.rating_count or _simulate_metric(item.rank, base=5000, step=120)
        heat_total = max(
            0,
            (100 - item.rank) * 100 + (score_val or 0.0) * 50 + review_count * 0.1
        )
        cover_url = item.cover_url or ''

        defaults = {
            'category': category,
            'publisher': publisher,
            'rating': rating,
            'download_count': download_count,
            'follow_count': follow_count,
            'review_count': review_count,
            'release_date': item.release_date or None,
            'description': f"自动导入：来源 3DM，榜单排名 #{item.rank}",
            'heat_total': heat_total,
            'heat_static': heat_total,
            'heat_dynamic': 0,
            'cover_image': cover_url if cover_url else None,
        }

        game, created = Game.objects.get_or_create(
            name=item.name,
            defaults=defaults
        )

        # 填充缺失字段或更新热度
        updated_fields = []
        for field, value in defaults.items():
            current = getattr(game, field, None)
            # 如果当前字段为空/0，用新值填充；热度始终刷新
            if field in ['heat_total', 'heat_static'] or current in [None, '', 0]:
                setattr(game, field, value)
                updated_fields.append(field)

        # 如果有抓取到封面且当前封面为空，补充封面
        if cover_url and (not game.cover_image or not getattr(game.cover_image, 'name', '')):
            game.cover_image = cover_url
            updated_fields.append('cover_image')

        if updated_fields:
            game.save(update_fields=list(set(updated_fields)))

        # 同步标签
        for tag_name in item.tags or []:
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            game.tags.add(tag)

        if created or updated_fields:
            synced += 1

    return synced
