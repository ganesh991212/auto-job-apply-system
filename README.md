# Auto Job Apply System

A comprehensive multi-service application for automated job applications with AI-powered resume matching.

## Architecture Overview

This system follows a microservices architecture with the following components:

- **Frontend**: Flutter Web application for user interface
- **Backend Services**:
  - Auth Service: Authentication and authorization
  - Core Service: Main job application logic
  - ML Service: Resume parsing and job matching
  - Payment Service: Subscription and billing management
- **Database**: PostgreSQL with proper schema and migrations
- **Infrastructure**: Docker Compose for local development

## Project Structure

```
/frontend/                 # Flutter Web UI
/backend/
  /auth/                  # FastAPI authentication service
  /core/                  # FastAPI core job application service
  /ml/                    # ML microservice for resume parsing
  /payment/               # Payment integration service
/db/                      # PostgreSQL schema and migrations
/infra/                   # Docker Compose and CI/CD setup
```

## Features

### For Candidates
- OAuth2 login (Google, Microsoft, Apple) + Email/OTP
- Profile setup with resume upload
- Automated job applications (5 per day limit)
- AI-powered job matching and resume enhancement
- Job application history and tracking
- Subscription management

### For Super Admins
- User management and role assignment
- Platform management (add/remove job portals)
- Unlimited job applications
- Global job logs and analytics
- System administration

## Technology Stack

- **Frontend**: Flutter Web
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **ML/AI**: spaCy, BERT, HuggingFace Transformers
- **Authentication**: OAuth2, JWT
- **Payment**: Stripe, Razorpay, PayPal
- **Security**: AES-256 encryption, bcrypt hashing
- **Infrastructure**: Docker, Docker Compose
- **CI/CD**: GitHub Actions / Azure DevOps

## Getting Started

1. Clone the repository
2. Install dependencies
3. Set up environment variables
4. Run with Docker Compose: `docker-compose up`

## Development

Each service can be developed and tested independently. See individual service README files for specific setup instructions.
