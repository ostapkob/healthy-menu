import logging
import sys
from typing import Any

import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


def setup_logging() -> None:
    """Настройка структурированного логирования в JSON формате."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


def get_logger() -> Any:
    """Получить логгер для использования в коде."""
    return structlog.get_logger()


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware для логирования HTTP-запросов."""

    async def dispatch(self, request: Request, call_next):
        logger = structlog.get_logger()
        
        # Генерируем correlation ID для трассировки
        correlation_id = request.headers.get("X-Correlation-ID", str(id(request)))
        
        # Логгируем начало запроса
        await logger.ainfo(
            "request_started",
            method=request.method,
            path=request.url.path,
            query=str(request.query_params),
            correlation_id=correlation_id,
            client_host=request.client.host if request.client else None,
        )
        
        try:
            response: Response = await call_next(request)
            
            # Логгируем завершение запроса
            await logger.ainfo(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                correlation_id=correlation_id,
            )
            
            return response
        except Exception as e:
            # Логгируем ошибку
            await logger.aerror(
                "request_error",
                method=request.method,
                path=request.url.path,
                error=str(e),
                correlation_id=correlation_id,
                exc_info=True,
            )
            raise
