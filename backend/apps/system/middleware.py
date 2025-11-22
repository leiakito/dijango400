"""
系统日志中间件
"""
import time
import json
from django.utils.deprecation import MiddlewareMixin
from .models import SysLog


class SystemLogMiddleware(MiddlewareMixin):
    """
    系统日志中间件
    记录API请求和响应
    """
    
    # 需要记录日志的路径前缀（记录所有API请求）
    LOG_PATHS = [
        '/api/v1/',
    ]
    
    # 需要排除的路径
    EXCLUDE_PATHS = [
        '/api/v1/system/logs/',  # 避免循环记录
        '/api/v1/system/health/',
        '/api/schema/',  # API文档
        '/api/docs/',    # API文档
    ]
    
    def should_log(self, path):
        """判断是否需要记录日志"""
        # 排除的路径
        for exclude_path in self.EXCLUDE_PATHS:
            if path.startswith(exclude_path):
                return False
        
        # 需要记录的路径
        for log_path in self.LOG_PATHS:
            if path.startswith(log_path):
                return True
        
        return False
    
    def process_request(self, request):
        """记录请求开始时间"""
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """记录请求日志"""
        if not self.should_log(request.path):
            return response
        
        try:
            # 计算请求耗时
            duration = None
            if hasattr(request, '_start_time'):
                duration = time.time() - request._start_time
            
            # 获取用户
            user = None
            if hasattr(request, 'user') and request.user.is_authenticated:
                user = request.user
            
            # 确定日志级别
            level = SysLog.Level.INFO
            if response.status_code >= 500:
                level = SysLog.Level.ERROR
            elif response.status_code >= 400:
                level = SysLog.Level.WARNING
            
            # 构建日志消息
            message = f"{request.method} {request.path} - {response.status_code}"
            if duration:
                message += f" ({duration:.3f}s)"
            
            # 构建上下文
            context = {
                'method': request.method,
                'path': request.path,
                'status_code': response.status_code,
                'duration': duration,
                'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
            }
            
            # 记录请求参数（GET）
            if request.GET:
                context['query_params'] = dict(request.GET)
            
            # 异步记录日志（避免影响响应速度）
            SysLog.objects.create(
                level=level,
                module='api',
                message=message,
                context=context,
                user=user,
                ip_address=self.get_client_ip(request)
            )
        
        except Exception as e:
            # 日志记录失败不应该影响正常响应
            print(f"日志记录失败: {str(e)}")
        
        return response
    
    def get_client_ip(self, request):
        """获取客户端IP地址"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def log_system_event(level, module, message, context=None, user=None):
    """
    手动记录系统事件的辅助函数
    
    Args:
        level: 日志级别 (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        module: 模块名称
        message: 日志消息
        context: 额外的上下文信息（字典）
        user: 相关用户
    """
    try:
        SysLog.objects.create(
            level=level,
            module=module,
            message=message,
            context=context or {},
            user=user
        )
    except Exception as e:
        print(f"系统日志记录失败: {str(e)}")

