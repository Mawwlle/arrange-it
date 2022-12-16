from pydantic import BaseModel


class RegistrationResponse(BaseModel):
    """Ответ на регистрацию"""

    message: str
    id: int


class VerificationResponse(BaseModel):
    """Ответ на регистрацию"""

    message: str
