# Lawsuit Management System - Complete Implementation Guide

## Project Structure Summary

```
LAWSUIT_MANAGEMENT_SYSTEM/
├── lawsuitapp/                    # Project settings
│   ├── __init__.py
│   ├── settings.py               # Django settings with JWT, Celery, Stripe
│   ├── urls.py                   # Main URL routing
│   ├── asgi.py
│   ├── wsgi.py
│   └── celery.py                 # Celery configuration
│
├── core/                          # Main application
│   ├── migrations/
│   ├── __init__.py
│   ├── models.py                 # Database models
│   ├── serializers.py            # DRF serializers
│   ├── views.py                  # API viewsets and views
│   ├── urls.py                   # API routes
│   ├── permissions.py            # Custom permission classes (RBAC)
│   ├── tasks.py                  # Celery email tasks
│   ├── admin.py                  # Django admin configuration
│   ├── apps.py
│   ├── tests.py
│   └── filters.py
│
├── templates/                     # HTML templates (if needed)
├── manage.py
├── requirements.txt              # Project dependencies
├── .env                          # Environment variables
├── .env.example                  # Example environment file
└── README.md                     # Setup instructions

```

## Step-by-Step Implementation

### Step 1: Project Setup

```bash
# Create project directory
mkdir lawsuit_management_system
cd lawsuit_management_system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Django Project Creation

```bash
# Create Django project
django-admin startproject lawsuitapp .

# Create Django app
python manage.py startapp core
```

### Step 3: Configure Settings

Replace content of `lawsuitapp/settings.py` with the provided settings.py file. This includes:
- Database configuration (PostgreSQL)
- JWT authentication setup
- Celery configuration
- Email backend
- Stripe API settings
- CORS configuration

### Step 4: Create Models

Replace content of `core/models.py` with the provided models.py file. Models include:
- UserProfile (with role-based distinction)
- CaseRequest (pending case submissions)
- Case (approved cases)
- RejectedCase (rejected submissions)
- CaseNote (case documentation)
- Payment (registration fee tracking)

### Step 5: Create Serializers

Replace content of `core/serializers.py` with the provided serializers.py file. Serializers handle:
- User registration and profiles
- Case request serialization
- Case serialization with nested notes
- Rejected case serialization
- Payment serialization

### Step 6: Implement Permissions

Replace content of `core/permissions.py` with the provided permissions.py file. Custom permissions:
- IsClient: Verify user is a client
- IsLawyer: Verify user is a lawyer
- IsClientOrReadOnly: Clients edit only their cases
- IsLawyerOrReadOnly: Lawyers approve/reject cases

### Step 7: Create Views

Replace content of `core/views.py` with the provided views.py file. ViewSets include:
- UserRegistrationView: Handle user registration
- UserProfileView: Manage user profiles
- CaseRequestViewSet: Client case submission and lawyer review
- CaseViewSet: Approved cases with approval/rejection actions
- RejectedCaseViewSet: View rejected cases
- CaseNoteViewSet: Add notes to cases
- PaymentViewSet: Handle payment processing

Key actions:
- `@action approve_case`: Lawyer approves case request
- `@action reject_case`: Lawyer rejects with reason
- `@action create_payment_intent`: Create Stripe payment
- `@action confirm_payment`: Confirm Stripe payment

### Step 8: Setup Celery Tasks

Replace content of `core/tasks.py` with the provided tasks.py file. Tasks:
- `send_case_approved_email`: Send approval notification with case details
- `send_case_rejected_email`: Send rejection notification with reason
- `send_payment_reminder_email`: Send payment reminders

### Step 9: Configure URLs

1. Replace `core/urls.py` with provided urls.py file
2. Replace `lawsuitapp/urls.py` with provided main-urls.py file (rename to urls.py)

URL structure:
- `/api/v1/auth/register/` - Registration
- `/api/v1/auth/token/` - Get JWT token
- `/api/v1/profile/` - User profile
- `/api/v1/case-requests/` - Case requests
- `/api/v1/cases/` - Approved cases
- `/api/v1/rejected-cases/` - Rejected cases
- `/api/v1/case-notes/` - Case notes
- `/api/v1/payments/` - Payments

### Step 10: Setup Admin Interface

Replace content of `core/admin.py` with the provided admin.py file for:
- User profile management
- Case request management
- Case management
- Payment tracking
- Rejected case viewing

### Step 11: Celery Configuration

Replace content of `lawsuitapp/celery.py` with provided celery.py file
Update `lawsuitapp/__init__.py` to load Celery on Django startup

### Step 12: Environment Variables

Create `.env` file from `.env.example` template with:
- Database credentials
- Email configuration
- Stripe keys
- Redis connection
- CORS settings

### Step 13: Database Setup

```bash
# Create PostgreSQL database
createdb lawsuit_db

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### Step 14: Start Services

**Terminal 1 - Redis:**
```bash
redis-server
```

**Terminal 2 - Celery Worker:**
```bash
celery -A lawsuitapp worker -l info
```

**Terminal 3 - Django Dev Server:**
```bash
python manage.py runserver
```

## API Usage Examples

### 1. User Registration (Client)

```bash
POST /api/v1/auth/register/
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123",
  "password_confirm": "securepass123",
  "role": "client",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response:**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "profile": {
    "id": 1,
    "role": "client"
  }
}
```

### 2. Get JWT Token

```bash
POST /api/v1/auth/token/
Content-Type: application/json

{
  "username": "johndoe",
  "password": "securepass123"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 3. Create Case Request (Client)

```bash
POST /api/v1/case-requests/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "title": "Divorce Settlement",
  "description": "Need assistance with property division and custody",
  "case_type": "Family Law",
  "amount_involved": "150000.00",
  "requested_lawyer_type": "Family Law Specialist"
}
```

**Response:**
```json
{
  "id": 1,
  "client": 1,
  "client_name": "johndoe",
  "title": "Divorce Settlement",
  "description": "Need assistance with property division and custody",
  "case_type": "Family Law",
  "status": "pending",
  "amount_involved": "150000.00",
  "created_at": "2024-11-07T10:30:00Z"
}
```

### 4. List Pending Cases (Lawyer)

```bash
GET /api/v1/case-requests/?status=pending
Authorization: Bearer <lawyer_token>
```

### 5. Approve Case (Lawyer)

```bash
POST /api/v1/cases/1/approve_case/
Authorization: Bearer <lawyer_token>
Content-Type: application/json

{
  "registration_fee": 1000.00
}
```

**Response:**
```json
{
  "message": "Case approved successfully",
  "case": {
    "id": 1,
    "case_number": "CASE-ABC12345",
    "status": "approved",
    "registration_fee": 1000.00,
    "lawyer": 2,
    "lawyer_name": "lawyername"
  }
}
```

**Celery Task Action:** Sends approval email to client asynchronously

### 6. Reject Case (Lawyer)

```bash
POST /api/v1/cases/1/reject_case/
Authorization: Bearer <lawyer_token>
Content-Type: application/json

{
  "rejection_reason": "Case outside our practice area"
}
```

**Celery Task Action:** Sends rejection email with reason to client asynchronously

### 7. Create Payment Intent (Client)

```bash
POST /api/v1/payments/1/create_payment_intent/
Authorization: Bearer <client_token>
```

**Response:**
```json
{
  "client_secret": "pi_1234567890...",
  "payment_intent_id": "pi_1234567890"
}
```

### 8. Confirm Payment (Client)

```bash
POST /api/v1/payments/1/confirm_payment/
Authorization: Bearer <client_token>
```

**Response:**
```json
{
  "message": "Payment confirmed successfully"
}
```

## Workflow Diagrams

### Client Workflow
```
Register → Create Case Request → Wait for Review → 
If Approved: Pay Fee → Track Case → Add Notes
If Rejected: View Reason → Can Resubmit
```

### Lawyer Workflow
```
Register → View Pending Cases → Review Details → 
Approve (Create Case + Send Email) OR 
Reject (Send Email + Store Reason) → 
Manage Approved Cases → Add Notes → Track Progress
```

## Key Features Implementation

### 1. JWT Authentication
- Uses `djangorestframework-simplejwt`
- Access tokens expire in 1 hour
- Refresh tokens expire in 1 day
- All endpoints require valid token (except registration and token endpoints)

### 2. RBAC Implementation
- UserProfile model stores role (client/lawyer)
- Custom permission classes check role
- ViewSet get_queryset() filters based on role
- Different endpoints available based on role

### 3. Asynchronous Email System
- `@shared_task` decorator marks functions as Celery tasks
- `.delay()` method sends task to Redis queue
- Worker processes tasks independently
- HTML email templates with professional formatting
- Automatic retry on failure

### 4. Case Management Flow
- Client submits CaseRequest
- Lawyer reviews and approves/rejects
- Approval: Creates Case entry, deletes CaseRequest, sends email, creates Payment
- Rejection: Creates RejectedCase entry, deletes CaseRequest, sends email with reason

### 5. Payment Integration
- Stripe PaymentIntent API for secure processing
- Payment model tracks transaction
- Case registration_fee_paid flag updates on success
- Payment status transitions (pending → completed/failed)

## Testing Checklist

- [ ] User registration (client and lawyer)
- [ ] JWT token generation and refresh
- [ ] Client can create case request
- [ ] Lawyer can view pending cases
- [ ] Lawyer can approve case (check email sent)
- [ ] Lawyer can reject case (check email with reason)
- [ ] Client can view approved cases
- [ ] Payment intent creation
- [ ] Payment confirmation
- [ ] Case notes creation
- [ ] Filter by status parameter
- [ ] CORS headers in response
- [ ] API documentation at /api/v1/docs/

## Production Deployment Checklist

- [ ] Set DEBUG = False
- [ ] Update SECRET_KEY with strong random value
- [ ] Configure allowed hosts
- [ ] Use production database credentials
- [ ] Setup HTTPS/SSL
- [ ] Configure email with production SMTP
- [ ] Setup Stripe production keys
- [ ] Configure CORS for production domain
- [ ] Setup database backups
- [ ] Configure Celery worker supervision (systemd/supervisor)
- [ ] Setup Redis persistence
- [ ] Configure logging and monitoring
- [ ] Run security checks: `python manage.py check --deploy`

## Troubleshooting Guide

**Issue: Emails not sending**
- Check EMAIL_BACKEND setting
- Verify Redis connection
- Check Celery worker is running
- Review Celery logs for errors

**Issue: Celery tasks not executing**
- Ensure Redis is accessible
- Check Celery worker console for registration of tasks
- Verify CELERY_BROKER_URL is correct

**Issue: Database migration errors**
- Run: `python manage.py makemigrations core`
- Then: `python manage.py migrate`

**Issue: JWT token not working**
- Ensure token is included in Authorization header
- Check token hasn't expired
- Verify refresh token hasn't expired
