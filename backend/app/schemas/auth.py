from pydantic import BaseModel, field_validator, Field
from typing import Optional
from app.models.user import UserRole
import phonenumbers
import re


def validate_phone_e164(v: str) -> str:
    """Parses and validates a phone number, returning E.164 format."""
    v = v.strip()
    if not v:
        raise ValueError("Phone number cannot be empty.")

    v_clean = re.sub(r'[()\-\s]', '', v)
    
    try:
       
        parsed = phonenumbers.parse(v_clean, "RU")
        if not phonenumbers.is_valid_number(parsed):
            raise ValueError("Invalid phone number.")

        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except phonenumbers.NumberParseException:
        raise ValueError("Invalid phone number format.")


class TokenPayload(BaseModel):
    """Pydantic model for the JWT content."""
    sub: str = Field(..., description="User ID (UUID)")
    role: UserRole = Field(..., description="User role (e.g., student, admin)")
    exp: float = Field(..., description="Expiration time (timestamp in seconds)")
    type: str = Field(..., description="Token type (access or refresh)")


class PhoneRequest(BaseModel):
    """Request to send a verification code."""
    phone: str
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return validate_phone_e164(v)

class CodeVerifyRequest(BaseModel):
    """Request to verify the SMS code."""
    phone: str
    code: str
    
    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        return validate_phone_e164(v)
    
    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v.isdigit() or len(v) != 6:
            raise ValueError("Code must be 6 digits.")
        return v

class RefreshTokenRequest(BaseModel):
    """A placeholder model for token requests where the token comes from a cookie."""
    pass


class TokenResponse(BaseModel):
    """Response with tokens."""
    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Access Token expiry in seconds")
    is_new_user: bool = Field(False, description="True if a new user was created")

class CodeRequestResponse(BaseModel):
    """Response after a successful code request."""
    message: str = Field(..., description="Status message.")
    expires_in: int = Field(..., description="Code expiry in seconds (e.g., 300)")
    debug_code: Optional[str] = Field(None, description="The generated code (only in DEBUG mode)")