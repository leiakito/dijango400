"""
Community Celery tasks
"""
from celery import shared_task
from django.db.models import Count, Sum, F
from django.utils import timezone
from datetime import timedelta
from .models import Topic, Post
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def update_topic_heat(self):
    """
    更新话题热度
    每小时执行一次
    """
    try:
        logger.info("Updating topic heat...")
        
        # 计算最近7天的活跃度
        cutoff_date = timezone.now() - timedelta(days=7)
        
        topics = Topic.objects.all()
        updated_count = 0
        
        for topic in topics:
            # 统计话题下的帖子和互动
            posts = Post.objects.filter(
                topics=topic,
                is_deleted=False,
                created_at__gte=cutoff_date
            )
            
            post_count = posts.count()
            total_likes = posts.aggregate(total=Sum('like_count'))['total'] or 0
            total_comments = posts.aggregate(total=Sum('comment_count'))['total'] or 0
            
            # 计算热度：帖子数 * 0.3 + 点赞数 * 0.4 + 评论数 * 0.3
            heat = post_count * 0.3 + total_likes * 0.4 + total_comments * 0.3
            
            # 更新话题
            topic.heat = heat
            topic.post_count = Post.objects.filter(topics=topic, is_deleted=False).count()
            topic.save(update_fields=['heat', 'post_count'])
            
            updated_count += 1
        
        logger.info(f"Updated heat for {updated_count} topics")
        
        return {'updated': updated_count}
    except Exception as e:
        logger.error(f"Topic heat update failed: {e}", exc_info=True)
        raise


@shared_task(bind=True)
def clean_deleted_posts(self):
    """
    清理已删除的帖子（物理删除）
    每周执行一次
    """
    try:
        logger.info("Cleaning deleted posts...")
        
        # 删除30天前标记为删除的帖子
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count = Post.objects.filter(
            is_deleted=True,
            updated_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"Cleaned {deleted_count} deleted posts")
        
        return {'deleted': deleted_count}
    except Exception as e:
        logger.error(f"Post cleanup failed: {e}", exc_info=True)
        raise

