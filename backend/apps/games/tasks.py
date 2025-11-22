"""
Game related Celery tasks
"""
import logging
from celery import shared_task

from .services import sync_3dm_single_player_ranking, sync_rankings_to_games

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_single_player_ranking(self):
    """
    同步 3DM 单机游戏排行榜 + 写入游戏列表
    """
    try:
        ranking_updated = sync_3dm_single_player_ranking()
        games_synced = sync_rankings_to_games()
        return {'ranking_updated': ranking_updated, 'games_synced': games_synced}
    except Exception as exc:  # noqa: broad-except
        logger.exception("同步单机游戏排行榜失败: %s", exc)
        raise self.retry(exc=exc, countdown=600)
