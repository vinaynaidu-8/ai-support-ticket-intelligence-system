from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.database.connection import Base, engine, get_db

from app.models.user import User
from app.models.ticket import Ticket
from app.models.ticket_message import TicketMessage
from app.models.ai_analysis import AIAnalysis

from app.schemas.user import UserCreate, UserLogin
from app.schemas.ticket import (
    TicketCreate,
    MessageCreate,
    MessageResponse,
    TicketStatusUpdate,
    TicketAssignment,
)
from app.schemas.ai_analysis import AIAnalysisResponse

from app.security.auth import get_current_user
from app.security.authorization import require_role
from app.security.jwt import create_access_token
from app.security.password import hash_password, verify_password

from app.services.llm.gemini import analyze_ticket
from app.services.ai_analysis import save_ai_analysis


app = FastAPI(title=settings.app_name)

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "message": f"{settings.app_name} is running",
        "environment": settings.app_env,
    }


@app.get("/db-test")
def database_test():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database": result.scalar()}


@app.post("/users")
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered",
        )

    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
    }

@app.post("/login")
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    if not verify_password(
        user_data.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@app.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "role": current_user.role,
    }

@app.get("/customer-area")
def customer_area(
    current_user: User = Depends(require_role("customer")),
):
    return {
        "message": "Customer access granted",
        "user": current_user.name,
    }

@app.get("/agent-area")
def agent_area(
    current_user: User = Depends(require_role("support_agent")),
):
    return {
        "message": "Support agent access granted",
        "user": current_user.name,
    }

@app.post("/tickets")
def create_ticket(
    ticket_data: TicketCreate,
    current_user: User = Depends(require_role("customer")),
    db: Session = Depends(get_db),
):
    ticket = Ticket(
        customer_id=current_user.id,
        subject=ticket_data.subject,
        description=ticket_data.description,
        category=ticket_data.category,
        priority=ticket_data.priority,
        status="open",
    )

    # Save ticket safely
    try:
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
    except Exception:
        db.rollback()
        raise

    # AI analysis is an enhancement.
    # Ticket creation should still succeed if Gemini fails.
    try:
        analysis = analyze_ticket(
            subject=ticket.subject,
            description=ticket.description,
            category=ticket.category,
            priority=ticket.priority,
        )

        save_ai_analysis(
            db=db,
            ticket_id=ticket.id,
            model_name="gemini-3.6-flash",
            summary=analysis.summary,
            suggested_category=analysis.suggested_category,
            suggested_priority=analysis.suggested_priority,
            suggested_response=analysis.suggested_response,
        )

    except Exception as e:
        print(f"AI analysis failed for ticket {ticket.id}: {e}")

    return {
        "id": ticket.id,
        "customer_id": ticket.customer_id,
        "subject": ticket.subject,
        "description": ticket.description,
        "category": ticket.category,
        "priority": ticket.priority,
        "status": ticket.status,
    }

@app.get("/tickets")
def get_my_tickets(
    current_user: User = Depends(require_role("customer")),
    db: Session = Depends(get_db),
):
    tickets = db.query(Ticket).filter(
        Ticket.customer_id == current_user.id
    ).all()

    return tickets

@app.get("/tickets/{ticket_id}")
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(require_role("customer")),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.customer_id == current_user.id,
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket

@app.post("/tickets/{ticket_id}/messages")
def create_ticket_message(
    ticket_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(require_role("customer")),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.customer_id == current_user.id,
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    message = TicketMessage(
        ticket_id=ticket.id,
        sender_id=current_user.id,
        message=message_data.message,
    )

    try:
        db.add(message)
        db.commit()
        db.refresh(message)
    except Exception:
        db.rollback()
        raise

    return message

@app.get(
    "/tickets/{ticket_id}/messages",
    response_model=list[MessageResponse],
)
def get_ticket_messages(
    ticket_id: int,
    current_user: User = Depends(require_role("customer")),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.customer_id == current_user.id,
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    messages = db.query(TicketMessage).filter(
        TicketMessage.ticket_id == ticket_id
    ).order_by(TicketMessage.created_at).all()

    return messages

@app.get("/agent/tickets")
def get_agent_tickets(
    current_user: User = Depends(require_role("support_agent")),
    db: Session = Depends(get_db),
):
    tickets = db.query(Ticket).filter(
        Ticket.assigned_agent_id == current_user.id
    ).all()

    return tickets

@app.get(
    "/agent/tickets/{ticket_id}/ai-analysis",
    response_model=AIAnalysisResponse,
)   
def get_ticket_ai_analysis(
    ticket_id: int,
    current_user: User = Depends(require_role("support_agent")),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.assigned_agent_id == current_user.id,
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found or not assigned to you",
        )

    analysis = db.query(AIAnalysis).filter(
        AIAnalysis.ticket_id == ticket_id
    ).first()

    if not analysis:
        raise HTTPException(
            status_code=404,
            detail="AI analysis not found",
        )

    return analysis

@app.patch("/tickets/{ticket_id}/assign")
def assign_ticket(
    ticket_id: int,
    assignment: TicketAssignment,
    current_user: User = Depends(require_role("support_agent")),
    db: Session = Depends(get_db),
):
    agent = db.query(User).filter(
        User.id == assignment.agent_id,
        User.role == "support_agent",
        User.is_active.is_(True),
    ).first()

    if not agent:
        raise HTTPException(
            status_code=404,
            detail="Support agent not found",
        )

    ticket = db.get(Ticket, ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    ticket.assigned_agent_id = agent.id

    db.commit()
    db.refresh(ticket)

    return ticket

@app.patch("/tickets/{ticket_id}/status")
def update_ticket_status(
    ticket_id: int,
    status_data: TicketStatusUpdate,
    current_user: User = Depends(require_role("support_agent")),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.assigned_agent_id == current_user.id,
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    ticket.status = status_data.status

    db.commit()
    db.refresh(ticket)

    return ticket

@app.post("/agent/tickets/{ticket_id}/messages")
def agent_create_ticket_message(
    ticket_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(require_role("support_agent")),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.assigned_agent_id == current_user.id,
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    message = TicketMessage(
        ticket_id=ticket.id,
        sender_id=current_user.id,
        message=message_data.message,
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@app.get(
    "/agent/tickets/{ticket_id}/messages",
    response_model=list[MessageResponse],
)
def agent_get_ticket_messages(
    ticket_id: int,
    current_user: User = Depends(require_role("support_agent")),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id,
        Ticket.assigned_agent_id == current_user.id,
    ).first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found or not assigned to you",
        )

    messages = db.query(TicketMessage).filter(
        TicketMessage.ticket_id == ticket_id
    ).order_by(TicketMessage.created_at.asc()).all()

    return messages