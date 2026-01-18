from django.contrib import admin
from core.models import UserProfile, CaseRequest, Case, RejectedCase, CaseNote, Payment


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'phone', 'city', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone']


@admin.register(CaseRequest)
class CaseRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'title', 'case_type', 'status', 'amount_involved', 'created_at']
    list_filter = ['status', 'case_type', 'created_at']
    search_fields = ['title', 'description', 'client__username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ['case_number', 'client', 'lawyer', 'title', 'case_type', 'status', 'registration_fee_paid', 'created_at']
    list_filter = ['status', 'case_type', 'registration_fee_paid', 'created_at']
    search_fields = ['case_number', 'title', 'client__username', 'lawyer__username']
    readonly_fields = ['case_number', 'created_at', 'updated_at']


@admin.register(RejectedCase)
class RejectedCaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'client', 'title', 'rejected_by', 'rejected_at']
    list_filter = ['rejected_at']
    search_fields = ['title', 'description', 'client__username', 'rejection_reason']
    readonly_fields = ['rejected_at']


@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'case', 'author', 'created_at']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'case__case_number']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'case', 'amount', 'status', 'paid_at', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['case__case_number', 'stripe_payment_intent_id']
    readonly_fields = ['created_at', 'paid_at']
