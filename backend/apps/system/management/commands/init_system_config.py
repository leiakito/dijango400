"""
初始化系统配置
"""
from django.core.management.base import BaseCommand
from apps.system.models import SysConfig


class Command(BaseCommand):
    help = '初始化系统配置'

    def handle(self, *args, **options):
        configs = [
            # 网站基础配置
            {
                'key': 'site.name',
                'value': '游戏推荐平台',
                'description': '网站名称',
                'is_public': True
            },
            {
                'key': 'site.description',
                'value': '专业的游戏推荐和攻略分享平台',
                'description': '网站描述',
                'is_public': True
            },
            {
                'key': 'site.keywords',
                'value': '游戏,推荐,攻略,社区',
                'description': '网站关键词',
                'is_public': True
            },
            {
                'key': 'site.logo',
                'value': '/static/logo.png',
                'description': '网站Logo地址',
                'is_public': True
            },
            
            # 用户相关配置
            {
                'key': 'user.registration.enabled',
                'value': 'true',
                'description': '是否允许用户注册',
                'is_public': True
            },
            {
                'key': 'user.password.min_length',
                'value': '8',
                'description': '密码最小长度',
                'is_public': False
            },
            {
                'key': 'user.verification.email',
                'value': 'false',
                'description': '是否需要邮箱验证',
                'is_public': False
            },
            
            # 内容审核配置
            {
                'key': 'content.review.auto_approve',
                'value': 'false',
                'description': '是否自动通过内容审核',
                'is_public': False
            },
            {
                'key': 'content.review.keywords',
                'value': '赌博,暴力,色情',
                'description': '敏感词列表（逗号分隔）',
                'is_public': False
            },
            
            # 推荐系统配置
            {
                'key': 'recommend.algorithm',
                'value': 'collaborative',
                'description': '推荐算法：collaborative/content_based/hybrid',
                'is_public': False
            },
            {
                'key': 'recommend.cache.ttl',
                'value': '3600',
                'description': '推荐结果缓存时间（秒）',
                'is_public': False
            },
            
            # 系统维护配置
            {
                'key': 'system.maintenance.mode',
                'value': 'false',
                'description': '系统维护模式',
                'is_public': True
            },
            {
                'key': 'system.maintenance.message',
                'value': '系统正在维护中，请稍后访问',
                'description': '维护模式提示信息',
                'is_public': True
            },
            {
                'key': 'system.log.retention_days',
                'value': '30',
                'description': '日志保留天数',
                'is_public': False
            },
            {
                'key': 'system.backup.auto_enabled',
                'value': 'true',
                'description': '是否启用自动备份',
                'is_public': False
            },
            {
                'key': 'system.backup.schedule',
                'value': '0 2 * * *',
                'description': '自动备份计划（Cron表达式）',
                'is_public': False
            },
            {
                'key': 'system.backup.retention_count',
                'value': '7',
                'description': '备份文件保留数量',
                'is_public': False
            },
            
            # 上传限制配置
            {
                'key': 'upload.max_size',
                'value': '10485760',
                'description': '最大上传文件大小（字节），默认10MB',
                'is_public': False
            },
            {
                'key': 'upload.allowed_types',
                'value': 'jpg,jpeg,png,gif,mp4',
                'description': '允许上传的文件类型',
                'is_public': False
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for config_data in configs:
            config, created = SysConfig.objects.update_or_create(
                key=config_data['key'],
                defaults={
                    'value': config_data['value'],
                    'description': config_data['description'],
                    'is_public': config_data['is_public']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'创建配置: {config.key}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'更新配置: {config.key}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n完成！创建 {created_count} 个配置，更新 {updated_count} 个配置'
            )
        )

