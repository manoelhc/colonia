"""ContextEnvironment model for Colonia - many-to-many relationship between contexts and environments."""

from sqlmodel import Field, SQLModel


class ContextEnvironment(SQLModel, table=True):
    """Context-Environment relationship table."""

    __tablename__ = "context_environments"

    context_id: int = Field(foreign_key="contexts.id", primary_key=True)
    environment_id: int = Field(foreign_key="environments.id", primary_key=True)
