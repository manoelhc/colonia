"""StackEnvironment model for Colonia - many-to-many relationship between stacks and environments."""

from sqlmodel import Field, SQLModel


class StackEnvironment(SQLModel, table=True):
    """Stack-Environment relationship table."""

    __tablename__ = "stack_environments"

    stack_id: int = Field(foreign_key="stacks.id", primary_key=True)
    environment_id: int = Field(foreign_key="environments.id", primary_key=True)
