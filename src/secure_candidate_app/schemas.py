from pydantic import BaseModel, EmailStr, ConfigDict


class UserRegister(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr


class VacancyCreate(BaseModel):
    title: str
    description: str


class VacancyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str


class ApplicantCreate(BaseModel):
    name: str
    email: EmailStr
    vacancy_id: int


class ApplicantResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    vacancy_id: int


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
