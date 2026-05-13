import os

from fastapi import FastAPI


class SecurityHeadersConfig:
    # Security headers configuration
    ENABLE_HSTS = os.getenv("ENABLE_HSTS", "false").lower() == "true"
    ENABLE_CSP = os.getenv("ENABLE_CSP", "false").lower() == "true"
    ENABLE_XSS_PROTECTION = os.getenv("ENABLE_XSS_PROTECTION", "true").lower() == "true"
    ENABLE_CONTENT_SECURITY_POLICY = (
        os.getenv("ENABLE_CONTENT_SECURITY_POLICY", "true").lower() == "true"
    )

    HSTS_MAX_AGE = 31536000  # 1 year
    HSTS_INCLUDE_SUBDOMAINS = True
    HSTS_PRELOAD = True

    CSP_DEFAULT_SRC = "'self'"
    CSP_SCRIPT_SRC = "'self'"
    CSP_STYLE_SRC = "'self' 'unsafe-inline'"
    CSP_IMG_SRC = "'self' data:"
    CSP_FONT_SRC = "'self'"
    CSP_CONNECT_SRC = "'self'"
    CSP_FRAME_SRC = "'none'"


def create_security_headers_middleware(app: FastAPI) -> None:
    """
    Create security headers middleware to protect against common web vulnerabilities.

    This middleware adds various security headers to HTTP responses:
    - HSTS (HTTP Strict Transport Security) for HTTPS enforcement
    - CSP (Content Security Policy) to prevent XSS attacks
    - XSS Protection header
    - Other security headers

    Headers are configurable through environment variables for flexibility
    between development and production environments.
    """

    @app.middleware("http")
    async def security_headers_middleware(request, call_next):
        response = await call_next(request)

        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if SecurityHeadersConfig.ENABLE_HSTS:
            hsts_value = f"max-age={SecurityHeadersConfig.HSTS_MAX_AGE}"
            if SecurityHeadersConfig.HSTS_INCLUDE_SUBDOMAINS:
                hsts_value += "; includeSubDomains"
            if SecurityHeadersConfig.HSTS_PRELOAD:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value

        if SecurityHeadersConfig.ENABLE_CONTENT_SECURITY_POLICY:
            csp_value = f"default-src {SecurityHeadersConfig.CSP_DEFAULT_SRC}; "
            csp_value += f"script-src {SecurityHeadersConfig.CSP_SCRIPT_SRC}; "
            csp_value += f"style-src {SecurityHeadersConfig.CSP_STYLE_SRC}; "
            csp_value += f"img-src {SecurityHeadersConfig.CSP_IMG_SRC}; "
            csp_value += f"font-src {SecurityHeadersConfig.CSP_FONT_SRC}; "
            csp_value += f"connect-src {SecurityHeadersConfig.CSP_CONNECT_SRC}; "
            csp_value += f"frame-src {SecurityHeadersConfig.CSP_FRAME_SRC}"
            response.headers["Content-Security-Policy"] = csp_value

        return response


def create_hsts_middleware(app: FastAPI) -> None:
    """
    Create HSTS (HTTP Strict Transport Security) middleware for production environments.

    HSTS forces browsers to use HTTPS connections for a specified period,
    protecting against protocol downgrade attacks and cookie hijacking.

    This is only enabled in production environments to avoid issues during
    development and testing.
    """
    if SecurityHeadersConfig.ENABLE_HSTS:

        @app.middleware("http")
        async def hsts_middleware(request, call_next):
            response = await call_next(request)

            # Add HSTS header
            hsts_value = f"max-age={SecurityHeadersConfig.HSTS_MAX_AGE}"
            if SecurityHeadersConfig.HSTS_INCLUDE_SUBDOMAINS:
                hsts_value += "; includeSubDomains"
            if SecurityHeadersConfig.HSTS_PRELOAD:
                hsts_value += "; preload"
            response.headers["Strict-Transport-Security"] = hsts_value

            return response


def create_csp_middleware(app: FastAPI) -> None:
    """
    Create Content Security Policy (CSP) middleware to prevent XSS attacks.

    CSP helps prevent cross-site scripting (XSS) attacks by specifying which
    sources of content are allowed to be loaded and executed by the browser.

    This is only enabled in production environments for optimal security.
    """
    if SecurityHeadersConfig.ENABLE_CONTENT_SECURITY_POLICY:

        @app.middleware("http")
        async def csp_middleware(request, call_next):
            response = await call_next(request)

            # Add Content Security Policy header
            csp_value = f"default-src {SecurityHeadersConfig.CSP_DEFAULT_SRC}; "
            csp_value += f"script-src {SecurityHeadersConfig.CSP_SCRIPT_SRC}; "
            csp_value += f"style-src {SecurityHeadersConfig.CSP_STYLE_SRC}; "
            csp_value += f"img-src {SecurityHeadersConfig.CSP_IMG_SRC}; "
            csp_value += f"font-src {SecurityHeadersConfig.CSP_FONT_SRC}; "
            csp_value += f"connect-src {SecurityHeadersConfig.CSP_CONNECT_SRC}; "
            csp_value += f"frame-src {SecurityHeadersConfig.CSP_FRAME_SRC}"
            response.headers["Content-Security-Policy"] = csp_value

            return response
