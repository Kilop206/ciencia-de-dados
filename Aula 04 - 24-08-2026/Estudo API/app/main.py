from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import func, select

from .database import get_db
from .models import Colaborador
from .schemas import ColaboradorCreate, ColaboradorResponse, ColaboradorUpdate


app = FastAPI()


@app.post(
    "/collaborators",
    response_model=ColaboradorResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_collaborator(
    collaborator: ColaboradorCreate,
    db: Session = Depends(get_db),
):
    db_collaborator = Colaborador(
        nome=collaborator.nome,
        matricula=collaborator.matricula,
        setor=collaborator.setor,
        cargo=collaborator.cargo,
    )

    db.add(db_collaborator)

    try:
        db.commit()
        db.refresh(db_collaborator)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Matrícula já cadastrada",
        )

    return db_collaborator


@app.get(
    "/collaborators",
    response_model=list[ColaboradorResponse],
)
def get_collaborators(
    db: Session = Depends(get_db),
):
    stmt = select(Colaborador)
    collaborators = db.scalars(stmt).all()

    return collaborators


@app.get("/collaborators/count-by-sector")
def count_collaborators_by_sector(
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            Colaborador.setor,
            func.count(Colaborador.id).label("quantidade"),
        )
        .group_by(Colaborador.setor)
        .order_by(Colaborador.setor)
    )

    results = db.execute(stmt).all()

    return [
        {
            "setor": setor,
            "quantidade": quantidade,
        }
        for setor, quantidade in results
    ]


@app.get(
    "/collaborators/{matricula}",
    response_model=ColaboradorResponse,
)
def get_collaborator(
    matricula: str,
    db: Session = Depends(get_db),
):
    stmt = select(Colaborador).where(
        Colaborador.matricula == matricula
    )

    collaborator = db.scalars(stmt).first()

    if collaborator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado",
        )

    return collaborator


@app.put(
    "/collaborators/{matricula}",
    response_model=ColaboradorResponse,
)
def update_collaborator(
    matricula: str,
    collaborator_data: ColaboradorUpdate,
    db: Session = Depends(get_db),
):
    stmt = select(Colaborador).where(
        Colaborador.matricula == matricula
    )

    collaborator = db.scalars(stmt).first()

    if collaborator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado",
        )

    collaborator.nome = collaborator_data.nome
    collaborator.matricula = collaborator_data.matricula
    collaborator.setor = collaborator_data.setor
    collaborator.cargo = collaborator_data.cargo

    try:
        db.commit()
        db.refresh(collaborator)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Matrícula já cadastrada",
        )

    return collaborator


@app.delete(
    "/collaborators/{matricula}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_collaborator(
    matricula: str,
    db: Session = Depends(get_db),
):
    stmt = select(Colaborador).where(
        Colaborador.matricula == matricula
    )

    collaborator = db.scalars(stmt).first()

    if collaborator is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Colaborador não encontrado",
        )

    db.delete(collaborator)
    db.commit()