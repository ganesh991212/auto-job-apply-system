# Auto Job Apply System - Setup Guide

## 🚀 Quick Start

This guide will help you set up and run the Auto Job Apply System on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download here](https://www.python.org/downloads/)
- **Docker & Docker Compose** - [Download here](https://docs.docker.com/get-docker/)
- **Flutter SDK** - [Download here](https://docs.flutter.dev/get-started/install)
- **Git** - [Download here](https://git-scm.com/downloads)

## 🛠️ Installation Steps

### 1. Clone and Setup Environment

```bash
# Navigate to your project directory
cd "c:\Users\Admin\Desktop\Auto-Apply Job"

# Copy environment file
copy .env.example .env

# Edit .env file with your actual configuration values
notepad .env
```

### 2. Automated Setup (Recommended)

Run the automated setup script:

```bash
python setup.py
```

This will:
- Check prerequisites
- Install all backend dependencies
- Setup Flutter web
- Initialize the database
- Start PostgreSQL

### 3. Manual Setup (Alternative)

If you prefer manual setup:

#### Backend Services Setup

```bash
# Auth Service
cd backend/auth
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Linux/Mac
pip install -r requirements.txt
cd ../..

# Core Service
cd backend/core
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd ../..

# ML Service
cd backend/ml
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
cd ../..

# Payment Service
cd backend/payment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
cd ../..
```

#### Frontend Setup

```bash
cd frontend
flutter config --enable-web
flutter pub get
cd ..
```

### 4. Database Setup

```bash
# Start PostgreSQL
docker-compose up -d postgres

# Wait for database to be ready (about 30 seconds)
# The database will be automatically initialized with the schema
```

## 🚀 Running the Application

### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose up

# Or run in background
docker-compose up -d
```

### Option 2: Individual Services (Development)

Open separate terminals for each service:

```bash
# Terminal 1: Database
docker-compose up postgres

# Terminal 2: Auth Service
cd backend/auth
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8001 --reload

# Terminal 3: Core Service
cd backend/core
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8002 --reload

# Terminal 4: ML Service
cd backend/ml
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8003 --reload

# Terminal 5: Payment Service
cd backend/payment
venv\Scripts\activate
uvicorn main:app --host 0.0.0.0 --port 8004 --reload

# Terminal 6: Frontend
cd frontend
flutter run -d web-server --web-port 3000
```

## 🌐 Access Points

Once running, you can access:

- **Frontend Application**: http://localhost:3000
- **Auth Service API**: http://localhost:8001/docs
- **Core Service API**: http://localhost:8002/docs
- **ML Service API**: http://localhost:8003/docs
- **Payment Service API**: http://localhost:8004/docs
- **Database**: localhost:5432 (postgres/postgres123)

## 🔧 Configuration

### Environment Variables

Update the `.env` file with your actual values:

```env
# Required for OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Required for email OTP
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Required for payments
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
```

### OAuth Setup

1. **Google OAuth**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google+ API
   - Create OAuth 2.0 credentials
   - Add `http://localhost:3000` to authorized origins

2. **Microsoft OAuth**:
   - Go to [Azure Portal](https://portal.azure.com/)
   - Register a new application
   - Configure redirect URIs

## 🧪 Testing

### Backend API Testing

```bash
# Test auth service
curl http://localhost:8001/health

# Test core service
curl http://localhost:8002/health

# Test ML service
curl http://localhost:8003/health

# Test payment service
curl http://localhost:8004/health
```

### Frontend Testing

```bash
cd frontend
flutter test
```

## 📊 Default Accounts

The system creates default accounts:

- **Super Admin**: admin@autojobapply.com / admin123
- **Test User**: user@example.com / user123

## 🔍 Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 3000, 5432, 8001-8004 are available
2. **Docker issues**: Restart Docker Desktop
3. **Flutter web issues**: Run `flutter clean && flutter pub get`
4. **Database connection**: Check if PostgreSQL container is running

### Logs

```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs auth-service
docker-compose logs core-service
```

## 🛡️ Security Notes

- Change all default passwords and secrets in production
- Use proper SSL certificates for HTTPS
- Configure proper CORS origins
- Set up proper database access controls
- Use environment-specific configuration files

## 📝 Next Steps

1. Complete your profile setup
2. Configure OAuth providers
3. Set up email SMTP for OTP
4. Configure payment providers
5. Test job application functionality

For detailed API documentation, visit the `/docs` endpoint of each service.
