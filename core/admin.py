from django.contrib import admin
from .models import UserProfile, CaseRequest, Case, RejectedCase, CaseNote, Payment

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'city')
    search_fields = ('user__username', 'user__email', 'phone')
    list_filter = ('role',)

@admin.register(CaseRequest)
class CaseRequestAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'case_type', 'status', 'amount_involved', 'created_at')
    list_filter = ('status', 'case_type')
    search_fields = ('title', 'description', 'client__username')

@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_number', 'title', 'client', 'lawyer', 'status', 'registration_fee_paid')
    list_filter = ('status', 'registration_fee_paid')
    search_fields = ('case_number', 'title', 'client__username', 'lawyer__username')

@admin.register(RejectedCase)
class RejectedCaseAdmin(admin.ModelAdmin):
    list_display = ('title', 'client', 'case_type', 'rejected_by', 'rejected_at')
    search_fields = ('title', 'client__username')

@admin.register(CaseNote)
class CaseNoteAdmin(admin.ModelAdmin):
    list_display = ('case', 'author', 'created_at')
    list_filter = ('created_at',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('case', 'amount', 'status', 'created_at')
    list_filter = ('status',)
