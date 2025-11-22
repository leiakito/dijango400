"""
推荐算法服务
实现静态热度、动态热度、总热度计算和个性化推荐
"""
import math
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from django.core.cache import cache
from .models import AlgoConfig, Recommendation, GameMetricsDaily, UserInterest
from apps.games.models import Game, Tag
from apps.community.models import Post, Reaction
import logging

logger = logging.getLogger(__name__)


class RecommendationService:
    """推荐算法服务类"""
    
    def __init__(self):
        self._config = None
    
    @property
    def config(self):
        """懒加载配置，避免在模块导入时访问数据库"""
        if self._config is None:
            self._config = AlgoConfig.get_config()
        return self._config
    
    def calculate_static_heat(self, game):
        """
        计算静态热度分
        H_static = w_d * D + w_f * F + w_r * R
        """
        w_d = self.config.weight_download
        w_f = self.config.weight_follow
        w_r = self.config.weight_review
        
        heat_static = (
            w_d * game.download_count +
            w_f * game.follow_count +
            w_r * game.review_count
        )
        
        return heat_static
    
    def calculate_dynamic_heat(self, game, days=30):
        """
        计算动态热度分（带时间衰减）
        H_dynamic = Σ (w_l * L + w_c * C) * exp(-λ * t)
        """
        w_l = self.config.weight_like
        w_c = self.config.weight_comment
        lambda_decay = self.config.decay_lambda
        
        # 获取游戏相关的帖子（最近N天）
        cutoff_date = timezone.now() - timedelta(days=days)
        posts = Post.objects.filter(
            game=game,
            is_deleted=False,
            created_at__gte=cutoff_date
        ).select_related('author')
        
        heat_dynamic = 0.0
        now = timezone.now()
        
        for post in posts:
            # 计算帖子的时间差（小时）
            time_diff = (now - post.created_at).total_seconds() / 3600
            
            # 计算衰减因子
            decay_factor = math.exp(-lambda_decay * time_diff)
            
            # 单帖分数
            post_score = w_l * post.like_count + w_c * post.comment_count
            
            # 累加衰减后的分数
            heat_dynamic += post_score * decay_factor
        
        return heat_dynamic
    
    def calculate_total_heat(self, game):
        """
        计算总热度分
        H_total = α * H_static + β * H_dynamic
        """
        alpha = self.config.alpha
        beta = self.config.beta
        
        heat_static = self.calculate_static_heat(game)
        heat_dynamic = self.calculate_dynamic_heat(game)
        heat_total = alpha * heat_static + beta * heat_dynamic
        
        return heat_static, heat_dynamic, heat_total
    
    def update_game_heat(self, game):
        """更新游戏的热度分数"""
        heat_static, heat_dynamic, heat_total = self.calculate_total_heat(game)
        
        game.heat_static = heat_static
        game.heat_dynamic = heat_dynamic
        game.heat_total = heat_total
        game.save(update_fields=['heat_static', 'heat_dynamic', 'heat_total'])
        
        logger.info(f"Updated heat for game {game.name}: static={heat_static:.2f}, dynamic={heat_dynamic:.2f}, total={heat_total:.2f}")
        
        return heat_static, heat_dynamic, heat_total
    
    def update_all_games_heat(self):
        """批量更新所有游戏的热度"""
        games = Game.objects.all()
        updated_count = 0
        
        for game in games:
            try:
                self.update_game_heat(game)
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating heat for game {game.id}: {e}")
        
        logger.info(f"Updated heat for {updated_count} games")
        return updated_count
    
    def get_hot_games(self, category=None, top_k=None):
        """
        获取热门游戏榜单
        """
        if top_k is None:
            top_k = self.config.top_k
        
        cache_key = f"hot_games:{category or 'all'}:{top_k}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        queryset = Game.objects.all()
        if category:
            queryset = queryset.filter(category=category)
        
        hot_games = queryset.order_by('-heat_total')[:top_k]
        
        # 缓存1小时
        cache.set(cache_key, list(hot_games), 3600)
        
        return hot_games
    
    def get_new_games(self, category=None, top_k=None):
        """
        获取最新游戏榜单
        """
        if top_k is None:
            top_k = self.config.top_k
        
        cache_key = f"new_games:{category or 'all'}:{top_k}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result
        
        queryset = Game.objects.all()
        if category:
            queryset = queryset.filter(category=category)
        
        new_games = queryset.order_by('-release_date', '-created_at')[:top_k]
        
        # 缓存1小时
        cache.set(cache_key, list(new_games), 3600)
        
        return new_games
    
    def calculate_user_interests(self, user):
        """
        计算用户兴趣向量
        基于用户的浏览、收藏、下载、点赞等行为
        """
        from apps.games.models import Collection
        from apps.content.models import StrategyCollection
        
        # 获取用户收藏的游戏
        collected_games = Game.objects.filter(
            collectors__user=user
        ).prefetch_related('tags')
        
        # 获取用户收藏的攻略关联的游戏
        strategy_games = Game.objects.filter(
            strategies__collectors__user=user
        ).prefetch_related('tags')
        
        # 获取用户点赞的帖子关联的游戏
        from django.contrib.contenttypes.models import ContentType
        
        post_content_type = ContentType.objects.get_for_model(Post)
        liked_post_ids = Reaction.objects.filter(
            user=user,
            type='like',
            content_type=post_content_type
        ).values_list('object_id', flat=True)
        
        liked_posts = Post.objects.filter(id__in=liked_post_ids).exclude(game__isnull=True)
        liked_game_ids = liked_posts.values_list('game_id', flat=True)
        liked_games = Game.objects.filter(id__in=liked_game_ids).prefetch_related('tags')
        
        # 统计标签权重
        tag_weights = {}
        
        # 收藏游戏权重最高
        for game in collected_games:
            for tag in game.tags.all():
                tag_weights[tag.id] = tag_weights.get(tag.id, 0) + 3.0
        
        # 收藏攻略的游戏权重次之
        for game in strategy_games:
            for tag in game.tags.all():
                tag_weights[tag.id] = tag_weights.get(tag.id, 0) + 2.0
        
        # 点赞帖子的游戏权重较低
        for game in liked_games:
            for tag in game.tags.all():
                tag_weights[tag.id] = tag_weights.get(tag.id, 0) + 1.0
        
        # 归一化权重
        if tag_weights:
            max_weight = max(tag_weights.values())
            if max_weight > 0:
                tag_weights = {k: v / max_weight for k, v in tag_weights.items()}
        
        return tag_weights
    
    def update_user_interests(self, user):
        """更新用户兴趣到数据库"""
        tag_weights = self.calculate_user_interests(user)
        
        # 删除旧的兴趣记录
        UserInterest.objects.filter(user=user).delete()
        
        # 创建新的兴趣记录
        interests = []
        for tag_id, weight in tag_weights.items():
            interests.append(UserInterest(
                user=user,
                tag_id=tag_id,
                weight=weight
            ))
        
        if interests:
            UserInterest.objects.bulk_create(interests)
        
        logger.info(f"Updated interests for user {user.username}: {len(interests)} tags")
        return tag_weights
    
    def calculate_similarity(self, user, game):
        """
        计算用户与游戏的相似度
        使用余弦相似度: cos(u, g) = Σ(u_i * g_i) / (||u|| * ||g||)
        """
        # 获取用户兴趣向量
        user_interests = UserInterest.objects.filter(user=user).select_related('tag')
        user_vector = {interest.tag_id: interest.weight for interest in user_interests}
        
        if not user_vector:
            return 0.0
        
        # 获取游戏标签向量（二进制）
        game_tags = set(game.tags.values_list('id', flat=True))
        
        if not game_tags:
            return 0.0
        
        # 计算点积
        dot_product = sum(user_vector.get(tag_id, 0) for tag_id in game_tags)
        
        # 计算向量模
        user_norm = math.sqrt(sum(w ** 2 for w in user_vector.values()))
        game_norm = math.sqrt(len(game_tags))
        
        if user_norm == 0 or game_norm == 0:
            return 0.0
        
        # 余弦相似度
        similarity = dot_product / (user_norm * game_norm)
        
        return similarity
    
    def generate_personal_recommendations(self, user, top_k=None):
        """
        生成个性化推荐（猜你喜欢）
        """
        if top_k is None:
            top_k = self.config.top_k
        
        # 更新用户兴趣
        self.update_user_interests(user)
        
        # 获取用户已收藏的游戏ID
        from apps.games.models import Collection
        collected_game_ids = Collection.objects.filter(user=user).values_list('game_id', flat=True)
        
        # 获取候选游戏（排除已收藏的）
        candidate_games = Game.objects.exclude(id__in=collected_game_ids)
        
        # 计算相似度
        recommendations = []
        for game in candidate_games:
            similarity = self.calculate_similarity(user, game)
            if similarity > 0:
                recommendations.append({
                    'game': game,
                    'score': similarity,
                    'reason': {
                        'type': 'tag_similarity',
                        'matched_tags': list(game.tags.filter(
                            id__in=UserInterest.objects.filter(user=user).values_list('tag_id', flat=True)
                        ).values_list('name', flat=True))
                    }
                })
        
        # 按相似度排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        recommendations = recommendations[:top_k]
        
        # 保存推荐记录
        Recommendation.objects.filter(user=user).delete()
        
        recommendation_objects = []
        for rec in recommendations:
            recommendation_objects.append(Recommendation(
                user=user,
                game=rec['game'],
                score=rec['score'],
                reason=rec['reason']
            ))
        
        if recommendation_objects:
            Recommendation.objects.bulk_create(recommendation_objects)
        
        logger.info(f"Generated {len(recommendations)} recommendations for user {user.username}")
        
        return recommendations
    
    def get_personal_recommendations(self, user, top_k=None, force_refresh=False):
        """
        获取用户的个性化推荐
        
        参数:
            user: 用户对象
            top_k: 返回的推荐数量
            force_refresh: 是否强制刷新（跳过缓存）
        """
        if top_k is None:
            top_k = self.config.top_k
        
        # 如果不强制刷新，检查缓存
        cache_key = f"personal_rec:{user.id}:{top_k}"
        if not force_refresh:
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
        
        # 从数据库获取
        recommendations = Recommendation.objects.filter(user=user).select_related('game').order_by('-score')[:top_k]
        
        # 如果没有推荐记录或者强制刷新，生成新的
        if not recommendations or force_refresh:
            self.generate_personal_recommendations(user, top_k)
            recommendations = Recommendation.objects.filter(user=user).select_related('game').order_by('-score')[:top_k]
        
        # 缓存30分钟
        cache.set(cache_key, list(recommendations), 1800)
        
        return recommendations
    
    @staticmethod
    def clear_user_recommendations_cache(user):
        """
        清除指定用户的推荐缓存
        在用户收藏/取消收藏等行为后调用
        """
        from django.core.cache import cache
        
        # 删除数据库中的推荐记录
        Recommendation.objects.filter(user=user).delete()
        
        # 清除用户兴趣缓存
        UserInterest.objects.filter(user=user).delete()
        
        # 清除Redis缓存（如果使用了Redis）
        # 由于Django的cache.keys()在某些后端不支持，我们使用固定的key列表
        common_top_k_values = [5, 10, 12, 15, 20]
        for k in common_top_k_values:
            cache_key = f"personal_rec:{user.id}:{k}"
            cache.delete(cache_key)


# 全局服务实例
recommendation_service = RecommendationService()

