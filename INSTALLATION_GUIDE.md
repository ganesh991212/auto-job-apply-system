# 🚀 Auto Job Apply System - Installation Guide

## Current Status
✅ Project structure created successfully
✅ All microservices code implemented
✅ Flutter Web frontend developed
✅ Database schema ready
✅ Docker configuration complete

## Required Installations

### 1. Python 3.11+ Installation
**Status**: ❌ Not installed

**Installation Steps**:
1. Download Python from: https://www.python.org/downloads/
2. Choose Python 3.11 or later
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Verify installation: `python --version`

### 2. Docker Desktop Installation
**Status**: ❌ Not installed

**Installation Steps**:
1. Download Docker Desktop from: https://docs.docker.com/desktop/install/windows-install/
2. Install Docker Desktop for Windows
3. Start Docker Desktop
4. Verify installation: `docker --version`

### 3. Flutter SDK Installation
**Status**: ❌ Not installed

**Installation Steps**:
1. Download Flutter from: https://docs.flutter.dev/get-started/install/windows
2. Extract to C:\flutter (or your preferred location)
3. Add C:\flutter\bin to your PATH environment variable
4. Run `flutter doctor` to verify installation
5. Enable web support: `flutter config --enable-web`

## 🔧 Quick Installation Commands

After installing the above tools, run these commands:

```powershell
# 1. Set up environment
copy .env.example .env

# 2. Install Python dependencies for all services
cd backend\auth
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..\..

cd backend\core
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..\..

cd backend\ml
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
deactivate
cd ..\..

cd backend\payment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..\..

# 3. Set up Flutter
cd frontend
flutter pub get
flutter config --enable-web
cd ..

# 4. Start the application
docker-compose up
```

## 🎯 What's Already Done

### ✅ Backend Services (FastAPI)
- **Auth Service** (Port 8001): OAuth2, JWT, Email/OTP login
- **Core Service** (Port 8002): Job applications, platform management
- **ML Service** (Port 8003): Resume parsing, job matching with AI
- **Payment Service** (Port 8004): Stripe, Razorpay, PayPal integration

### ✅ Frontend (Flutter Web)
- **Login System**: OAuth + Email/OTP options
- **Profile Setup**: Resume upload, skills, platform credentials
- **Candidate Dashboard**: Job matches, application stats
- **Admin Dashboard**: User management, system overview
- **Job History**: Application tracking with filters
- **Payment UI**: Subscription plans and billing

### ✅ Database (PostgreSQL)
- Complete schema with all tables
- User authentication and profiles
- Job applications and history
- Payment and subscription management
- Audit logging and security

### ✅ Security Features
- AES-256 encryption for sensitive data
- JWT token authentication
- bcrypt password hashing
- Role-based access control
- Audit logging

## 🚀 Next Steps After Installation

1. **Install Prerequisites** (Python, Docker, Flutter)
2. **Configure Environment** (Update .env file)
3. **Start Services** (`docker-compose up`)
4. **Access Application** (http://localhost:3000)

## 📱 Application Features

### For Candidates:
- 🔐 Secure login (OAuth + Email/OTP)
- 📄 Resume upload and AI analysis
- 🎯 AI-powered job matching
- 🤖 Automated job applications (5/day limit)
- 📊 Application tracking and history
- 💳 Subscription management

### For Super Admins:
- 👥 User management
- 🏢 Platform management
- 📈 System analytics
- 🚀 Unlimited job applications
- 🔍 Global job logs

## 🛠️ Development Mode

For development, you can run services individually:
- Auth: `uvicorn main:app --port 8001 --reload`
- Core: `uvicorn main:app --port 8002 --reload`
- ML: `uvicorn main:app --port 8003 --reload`
- Payment: `uvicorn main:app --port 8004 --reload`
- Frontend: `flutter run -d web-server --web-port 3000`

The project is ready for installation! Please install Python, Docker, and Flutter first, then we can proceed with the setup.
