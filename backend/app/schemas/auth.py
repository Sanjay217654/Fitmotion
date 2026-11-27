from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.models.enums import FitnessGoal, FitnessLevel


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    confirm_password: str
    age: int = Field(ge=13, le=120)
    gender: str | None = Field(default=None, max_length=50)
    height_cm: float = Field(gt=0, le=300)
    weight_kg: float = Field(gt=0, le=500)
    sport: str = Field(min_length=2, max_length=80)
    fitness_level: FitnessLevel
    fitness_goal: FitnessGoal

    @model_validator(mode="after")
    def passwords_match_and_are_reasonable(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        if not any(char.isalpha() for char in self.password) or not any(char.isdigit() for char in self.password):
            raise ValueError("Password must include at least one letter and one number.")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    age: int | None
    gender: str | None
    height_cm: float | None
    weight_kg: float | None
    sport: str | None
    fitness_level: FitnessLevel | None
    fitness_goal: FitnessGoal | None
    profile_image: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
