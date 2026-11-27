from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import FitnessGoal, FitnessLevel


class UserUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None
    age: int | None = Field(default=None, ge=13, le=120)
    gender: str | None = Field(default=None, max_length=50)
    height_cm: float | None = Field(default=None, gt=0, le=300)
    weight_kg: float | None = Field(default=None, gt=0, le=500)
    sport: str | None = Field(default=None, min_length=2, max_length=80)
    fitness_level: FitnessLevel | None = None
    fitness_goal: FitnessGoal | None = None


class PasswordChangeRequest(BaseModel):
    current_password: str = Field(min_length=1, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def require_letter_and_number(cls, value: str) -> str:
        if not any(char.isalpha() for char in value) or not any(char.isdigit() for char in value):
            raise ValueError("Password must include at least one letter and one number.")
        return value
