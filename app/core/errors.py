from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    409: "conflict",
    422: "validation_error",
    500: "internal_server_error",
}

def build_error_response(status_code, message, details=None):
    payload = {
        "error": {
            "status": status_code,
            "code": ERROR_CODES.get(status_code, "error"),
            "message": message,
        }
    }

    if details is not None:
        payload["error"]["details"] = details

    return JSONResponse(status_code=status_code, content=payload)

def register_exception_handlers(app):
    @app.exception_handler(HTTPException)
    async def handle_http_exception(request, exc):
        if isinstance(exc.detail, str):
            return build_error_response(exc.status_code, exc.detail)

        return build_error_response(exc.status_code, "Request failed", exc.detail)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_exception(request, exc):
        return build_error_response(422, "Validation failed", exc.errors())

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request, exc):
        return build_error_response(500, "Internal server error")
