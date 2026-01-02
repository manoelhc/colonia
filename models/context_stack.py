"""ContextStack model for Colonia - many-to-many relationship between contexts and stacks."""

from sqlmodel import Field, SQLModel


class ContextStack(SQLModel, table=True):
    """Context-Stack relationship table."""

    __tablename__ = "context_stacks"

    context_id: int = Field(foreign_key="contexts.id", primary_key=True)
    stack_id: int = Field(foreign_key="stacks.id", primary_key=True)
