"""
Recommendations Celery tasks
"""
from celery import shared_task
from .services import recommendation_service
from apps.users.models import User
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def generate_all_recommendations(self):
    """
    为所有用户生成推荐
    每日凌晨3:30执行
    """
    try:
        logger.info("Starting recommendation generation for all users...")
        
        # 获取所有活跃用户
        users = User.objects.filter(status=User.Status.NORMAL)
        
        success_count = 0
        error_count = 0
        
        for user in users:
            try:
                recommendation_service.generate_personal_recommendations(user)
                success_count += 1
            except Exception as e:
                logger.error(f"Error generating recommendations for user {user.id}: {e}")
                error_count += 1
        
        logger.info(f"Recommendation generation completed: {success_count} success, {error_count} errors")
        
        return {
            'total_users': users.count(),
            'success': success_count,
            'errors': error_count
        }
    except Exception as e:
        logger.error(f"Recommendation generation task failed: {e}", exc_info=True)
        raise


@shared_task(bind=True)
def update_user_interests_batch(self, user_ids=None):
    """
    批量更新用户兴趣
    """
    try:
        if user_ids:
            users = User.objects.filter(id__in=user_ids)
        else:
            users = User.objects.filter(status=User.Status.NORMAL)
        
        updated_count = 0
        
        for user in users:
            try:
                recommendation_service.update_user_interests(user)
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating interests for user {user.id}: {e}")
        
        logger.info(f"Updated interests for {updated_count} users")
        
        return {'updated': updated_count}
    except Exception as e:
        logger.error(f"Batch interest update failed: {e}", exc_info=True)
        raise

