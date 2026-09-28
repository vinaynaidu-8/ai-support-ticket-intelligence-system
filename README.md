# AI Support Ticket System

A backend support-ticket management system built with FastAPI, PostgreSQL, SQLAlchemy, JWT authentication, role-based authorization, and Gemini AI.

## Features

- User registration and login
- JWT-based authentication
- Role-based authorization
- Customer ticket creation and retrieval
- Customer ticket ownership protection
- Support-agent ticket assignment
- Ticket status management
- Customer and agent conversations
- Gemini AI ticket analysis
- AI-generated:
  - Ticket summary
  - Suggested category
  - Suggested priority
  - Suggested response
- AI analysis stored in PostgreSQL
- Transaction rollback protection
- Pydantic request/response validation
- Interactive Swagger API documentation

## Architecture

```text
Customer
   |
   v
FastAPI API
   |
   +---- Authentication / Authorization
   |
   +---- Ticket Management
   |
   +---- PostgreSQL
   |
   +---- Gemini AI
             |
             v
       AI Ticket Analysis
             |
             v
       PostgreSQL
             |
             v
        Support Agent