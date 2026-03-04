from pydantic import BaseModel


class ApiError(BaseModel):
    status: int
    code: str
    message: str
    details: object | None = None


class ErrorResponse(BaseModel):
    error: ApiError
