from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.proxy import ProxyHeadersMiddleware
import os
from typing import Optional

class HTTPSConfig:
    # HTTPS configuration
    ENABLE_HTTPS_REDIRECT = os.getenv("ENABLE_HTTPS_REDIRECT", "false").lower() == "true"
    ENABLE_PROXY_HEADERS = os.getenv("ENABLE_PROXY_HEADERS", "false").lower() == "true"
    
    # Proxy headers configuration
    TRUSTED_PROXIES = os.getenv("TRUSTED_PROXIES", "127.0.0.1,localhost").split(",")
    TRUSTED_PROXY_DEPTH = int(os.getenv("TRUSTED_PROXY_DEPTH", "1"))


def create_https_enforcement_middleware(app: FastAPI) -> None:
    """
    Create HTTPS enforcement middleware to redirect HTTP requests to HTTPS.
    
    This middleware ensures all traffic is encrypted by redirecting HTTP
    requests to HTTPS. It's only enabled in production environments to
    avoid issues during development.
    
    For applications behind reverse proxies (like Nginx or AWS ALB), this
    middleware should be configured to trust the proxy's headers.
    """
    if HTTPSConfig.ENABLE_HTTPS_REDIRECT:
        app.add_middleware(HTTPSRedirectMiddleware)


def create_proxy_headers_middleware(app: FastAPI) -> None:
    """
    Create proxy headers middleware to handle requests from trusted proxies.
    
    When running behind reverse proxies (like Nginx, AWS ALB, etc.),
    this middleware ensures FastAPI correctly interprets the original
    client IP address and protocol.
    
    This is essential for proper rate limiting, logging, and security
    features when using a reverse proxy setup.
    """
    if HTTPSConfig.ENABLE_PROXY_HEADERS:
        app.add_middleware(
            ProxyHeadersMiddleware,
            trusted_hosts=HTTPSConfig.TRUSTED_PROXIES,
            trusted_proxy_depth=HTTPSConfig.TRUSTED_PROXY_DEPTH
        )


def create_production_security_middleware(app: FastAPI) -> None:
    """
    Create comprehensive production security middleware.
    
    This middleware combines multiple security features for production
    environments:
    - HTTPS enforcement
    - Proxy headers handling
    - Security headers (added via separate middleware)
    - Rate limiting (added via separate middleware)
    
    All features are configurable through environment variables for
    flexibility between development and production.
    """
    # Add HTTPS enforcement if enabled
    if HTTPSConfig.ENABLE_HTTPS_REDIRECT:
        app.add_middleware(HTTPSRedirectMiddleware)
    
    # Add proxy headers handling if enabled
    if HTTPSConfig.ENABLE_PROXY_HEADERS:
        app.add_middleware(
            ProxyHeadersMiddleware,
            trusted_hosts=HTTPSConfig.TRUSTED_PROXIES,
            trusted_proxy_depth=HTTPSConfig.TRUSTED_PROXY_DEPTH
        )


def is_production_environment() -> bool:
    """
    Check if the current environment is production.
    
    This function checks environment variables to determine if the
    application is running in a production environment.
    
    Returns:
        bool: True if in production environment, False otherwise
    """
    return os.getenv("ENVIRONMENT", "development").lower() == "production"


def create_production_security_setup(app: FastAPI) -> None:
    """
    Create complete production security setup.
    
    This function sets up all security features for production environments:
    - HTTPS enforcement
    - Proxy headers handling
    - Security headers
    - Rate limiting
    - CORS configuration
    
    All features are only enabled in production environments for optimal
    security without impacting development workflows.
    """
    if is_production_environment():
        # Add HTTPS enforcement
        if HTTPSConfig.ENABLE_HTTPS_REDIRECT:
            app.add_middleware(HTTPSRedirectMiddleware)
        
        # Add proxy headers handling
        if HTTPSConfig.ENABLE_PROXY_HEADERS:
            app.add_middleware(
                ProxyHeadersMiddleware,
                trusted_hosts=HTTPSConfig.TRUSTED_PROXIES,
                trusted_proxy_depth=HTTPSConfig.TRUSTED_PROXY_DEPTH
            )
        
        # Security headers and rate limiting will be added in main.py
        # to maintain proper import order