"""
自定义异常处理
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    自定义异常处理器，返回 RFC7807 风格的错误响应
    """
    # 调用 DRF 默认的异常处理器
    response = exception_handler(exc, context)
    
    if response is not None:
        # 标准化错误响应格式
        custom_response_data = {
            'type': 'about:blank',
            'title': get_error_title(exc),
            'status': response.status_code,
            'detail': get_error_detail(response.data),
        }
        
        # 添加额外的上下文信息
        if hasattr(exc, 'get_codes'):
            custom_response_data['code'] = exc.get_codes()
        
        response.data = custom_response_data
        
        # 记录错误日志
        if response.status_code >= 500:
            logger.error(
                f"Server error: {exc}",
                exc_info=True,
                extra={'context': context}
            )
    else:
        # 处理 Django 原生异常
        if isinstance(exc, DjangoValidationError):
            response = Response({
                'type': 'about:blank',
                'title': 'Validation Error',
                'status': status.HTTP_400_BAD_REQUEST,
                'detail': str(exc),
            }, status=status.HTTP_400_BAD_REQUEST)
        elif isinstance(exc, Http404):
            response = Response({
                'type': 'about:blank',
                'title': 'Not Found',
                'status': status.HTTP_404_NOT_FOUND,
                'detail': 'The requested resource was not found.',
            }, status=status.HTTP_404_NOT_FOUND)
        else:
            # 未处理的异常
            logger.error(
                f"Unhandled exception: {exc}",
                exc_info=True,
                extra={'context': context}
            )
            response = Response({
                'type': 'about:blank',
                'title': 'Internal Server Error',
                'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                'detail': 'An unexpected error occurred.',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return response


def get_error_title(exc):
    """获取错误标题"""
    if hasattr(exc, 'default_detail'):
        return str(exc.default_detail)
    return exc.__class__.__name__


def get_error_detail(data):
    """提取错误详情"""
    if isinstance(data, dict):
        # 如果是字典，提取第一个错误信息
        if 'detail' in data:
            return data['detail']
        # 提取字段错误
        errors = []
        for field, messages in data.items():
            if isinstance(messages, list):
                errors.append(f"{field}: {', '.join(str(m) for m in messages)}")
            else:
                errors.append(f"{field}: {messages}")
        return '; '.join(errors)
    elif isinstance(data, list):
        return ', '.join(str(item) for item in data)
    return str(data)

