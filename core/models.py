from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

# User Roles
ROLE_CHOICES = [
    ('client', 'Client'),
    ('lawyer', 'Lawyer'),
]

# Case Status
CASE_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]


class UserProfile(models.Model):
    """Extended user profile with role information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    zipcode = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class CaseRequest(models.Model):
    """Model for case requests filed by clients"""
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='case_requests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    case_type = models.CharField(max_length=100)  # e.g., Civil, Criminal, Corporate, etc.
    status = models.CharField(max_length=20, choices=CASE_STATUS_CHOICES, default='pending')
    documents = models.FileField(upload_to='case_documents/', blank=True, null=True)
    amount_involved = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0)])
    requested_lawyer_type = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Case Request: {self.title} - {self.client.username}"


class Case(models.Model):
    """Model for approved cases linked to both client and lawyer"""
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases_as_client')
    lawyer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cases_as_lawyer')
    case_request = models.OneToOneField(CaseRequest, on_delete=models.CASCADE, related_name='approved_case')
    case_number = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    case_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=CASE_STATUS_CHOICES, default='approved')
    documents = models.FileField(upload_to='case_documents/', blank=True, null=True)
    amount_involved = models.DecimalField(max_digits=15, decimal_places=2)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    registration_fee_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Case #{self.case_number} - {self.client.username}"


class RejectedCase(models.Model):
    """Model for rejected case requests"""
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rejected_cases')
    case_request = models.OneToOneField(CaseRequest, on_delete=models.CASCADE, related_name='rejection')
    title = models.CharField(max_length=255)
    description = models.TextField()
    case_type = models.CharField(max_length=100)
    rejection_reason = models.TextField()
    rejected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='rejected_cases_as_lawyer')
    rejected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-rejected_at']

    def __str__(self):
        return f"Rejected Case: {self.title} - {self.client.username}"


class CaseNote(models.Model):
    """Model for notes on cases"""
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note on Case #{self.case.case_number}"


class Payment(models.Model):
    """Model for handling payments"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    case = models.OneToOneField(Case, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True, null=True)
    paid_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Case #{self.case.case_number} - {self.status}"
