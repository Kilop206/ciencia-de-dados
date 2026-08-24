from pydantic import BaseModel, EmailStr


class ColaboradorCreate(BaseModel):
    nome: str
    matricula: str
    setor: str
    cargo: str


class ColaboradorUpdate(BaseModel):
    nome: str
    matricula: str
    setor: str
    cargo: str


class ColaboradorResponse(BaseModel):
    id: int
    nome: str
    matricula: str
    setor: str
    cargo: str


    model_config = {
        "from_attributes": True
    }