from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class TicketCreate(BaseModel):

    subject: str

    description: str

    category: str

    priority: str


class MessageCreate(BaseModel):

    message: str


class MessageResponse(BaseModel):

    id: int

    ticket_id: int

    sender_id: int

    message: str

    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class TicketStatusUpdate(BaseModel):

    status: Literal["open", "in_progress", "resolved", "closed"]


class TicketAssignment(BaseModel):

    agent_id: int