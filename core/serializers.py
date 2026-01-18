from rest_framework import serializers
from django.contrib.auth.models import User
from core.models import (
    UserProfile, CaseRequest, Case, RejectedCase, CaseNote, Payment
)


class UserProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email')

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user_id', 'username', 'email', 'role', 'phone', 'address',
            'city', 'state', 'zipcode', 'bio', 'profile_picture', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profile']
        read_only_fields = ['id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    role = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name', 'role']

    def validate(self, data):
        if data['password'] != data.pop('password_confirm'):
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, role=role)
        return user


class CaseRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.username', read_only=True)
    client_email = serializers.CharField(source='client.email', read_only=True)

    class Meta:
        model = CaseRequest
        fields = [
            'id', 'client', 'client_name', 'client_email', 'title', 'description',
            'case_type', 'status', 'documents', 'amount_involved', 'requested_lawyer_type',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'client', 'created_at', 'updated_at']


class CaseNoteSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = CaseNote
        fields = ['id', 'case', 'author', 'author_name', 'content', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']


class CaseSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.username', read_only=True)
    lawyer_name = serializers.CharField(source='lawyer.username', read_only=True, allow_null=True)
    notes = CaseNoteSerializer(many=True, read_only=True)
    payment = serializers.SerializerMethodField()

    class Meta:
        model = Case
        fields = [
            'id', 'client', 'client_name', 'lawyer', 'lawyer_name', 'case_request',
            'case_number', 'title', 'description', 'case_type', 'status', 'documents',
            'amount_involved', 'registration_fee', 'registration_fee_paid', 'notes', 'payment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'case_number', 'created_at', 'updated_at']

    def get_payment(self, obj):
        try:
            payment = obj.payment
            return PaymentSerializer(payment).data
        except Payment.DoesNotExist:
            return None


class RejectedCaseSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.username', read_only=True)
    rejected_by_name = serializers.CharField(source='rejected_by.username', read_only=True, allow_null=True)

    class Meta:
        model = RejectedCase
        fields = [
            'id', 'client', 'client_name', 'case_request', 'title', 'description',
            'case_type', 'rejection_reason', 'rejected_by', 'rejected_by_name', 'rejected_at'
        ]
        read_only_fields = ['id', 'rejected_at']


class PaymentSerializer(serializers.ModelSerializer):
    case_number = serializers.CharField(source='case.case_number', read_only=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'case', 'case_number', 'amount', 'status',
            'stripe_payment_intent_id', 'paid_at', 'created_at'
        ]
        read_only_fields = ['id', 'paid_at', 'created_at']
