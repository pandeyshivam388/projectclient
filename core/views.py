from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import uuid
import stripe
from django.conf import settings

from core.models import (
    UserProfile, CaseRequest, Case, RejectedCase, CaseNote, Payment, User
)
from core.serializers import (
    UserSerializer, UserRegistrationSerializer, UserProfileSerializer,
    CaseRequestSerializer, CaseSerializer, RejectedCaseSerializer, CaseNoteSerializer, PaymentSerializer
)
from core.permissions import IsClient, IsLawyer, IsClientOrReadOnly, IsLawyerOrReadOnly
from core.tasks import send_case_approved_email, send_case_rejected_email, send_payment_reminder_email

stripe.api_key = settings.STRIPE_SECRET_KEY


class UserRegistrationView(generics.CreateAPIView):
    """Register new user (client or lawyer)"""
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class CaseRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for case requests
    - Clients can create case requests
    - Lawyers can view and respond to case requests
    """
    serializer_class = CaseRequestSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'case_type']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'amount_involved']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'client':
            # Clients see only their own case requests
            return CaseRequest.objects.filter(client=user)
        elif user.profile.role == 'lawyer':
            # Lawyers see all case requests with pending status
            return CaseRequest.objects.filter(status='pending')
        return CaseRequest.objects.none()

    def perform_create(self, serializer):
        if self.request.user.profile.role != 'client':
            return Response(
                {'error': 'Only clients can file cases'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save(client=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[IsClient])
    def my_cases(self, request):
        """Get all case requests for current client"""
        case_requests = CaseRequest.objects.filter(client=request.user)
        serializer = self.get_serializer(case_requests, many=True)
        return Response(serializer.data)


class CaseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for approved cases
    - Clients can view their approved cases
    - Lawyers can view cases assigned to them
    """
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'case_number']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'client':
            return Case.objects.filter(client=user)
        elif user.profile.role == 'lawyer':
            return Case.objects.filter(lawyer=user)
        return Case.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsLawyer])
    def approve_case(self, request, pk=None):
        """Lawyer approves a case request"""
        case_request = get_object_or_404(CaseRequest, pk=pk)
        
        if case_request.status != 'pending':
            return Response(
                {'error': 'Only pending case requests can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a new Case record
        case_number = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        registration_fee = request.data.get('registration_fee', 500.00)
        
        case = Case.objects.create(
            client=case_request.client,
            lawyer=request.user,
            case_request=case_request,
            case_number=case_number,
            title=case_request.title,
            description=case_request.description,
            case_type=case_request.case_type,
            documents=case_request.documents,
            amount_involved=case_request.amount_involved,
            registration_fee=registration_fee
        )

        # Update case request status
        case_request.status = 'approved'
        case_request.save()

        # Send approval email asynchronously
        send_case_approved_email.delay(case.id)

        # Delete case request
        case_request.delete()

        serializer = CaseSerializer(case)
        return Response(
            {'message': 'Case approved successfully', 'case': serializer.data},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], permission_classes=[IsLawyer])
    def reject_case(self, request, pk=None):
        """Lawyer rejects a case request"""
        case_request = get_object_or_404(CaseRequest, pk=pk)
        
        if case_request.status != 'pending':
            return Response(
                {'error': 'Only pending case requests can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )

        rejection_reason = request.data.get('rejection_reason', 'No reason provided')

        # Create rejected case record
        rejected_case = RejectedCase.objects.create(
            client=case_request.client,
            case_request=case_request,
            title=case_request.title,
            description=case_request.description,
            case_type=case_request.case_type,
            rejection_reason=rejection_reason,
            rejected_by=request.user
        )

        # Update case request status
        case_request.status = 'rejected'
        case_request.save()

        # Send rejection email asynchronously
        send_case_rejected_email.delay(rejected_case.id)

        # Delete case request
        case_request.delete()

        serializer = RejectedCaseSerializer(rejected_case)
        return Response(
            {'message': 'Case rejected successfully', 'rejected_case': serializer.data},
            status=status.HTTP_201_CREATED
        )


class RejectedCaseViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing rejected cases"""
    serializer_class = RejectedCaseSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['rejected_at']
    ordering = ['-rejected_at']

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'client':
            return RejectedCase.objects.filter(client=user)
        elif user.profile.role == 'lawyer':
            return RejectedCase.objects.filter(rejected_by=user)
        return RejectedCase.objects.none()


class CaseNoteViewSet(viewsets.ModelViewSet):
    """ViewSet for case notes"""
    serializer_class = CaseNoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        case_id = self.kwargs.get('case_id')
        return CaseNote.objects.filter(case_id=case_id)

    def perform_create(self, serializer):
        case_id = self.kwargs.get('case_id')
        case = get_object_or_404(Case, id=case_id)
        serializer.save(author=self.request.user, case=case)


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for handling payments"""
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.profile.role == 'client':
            return Payment.objects.filter(case__client=user)
        elif user.profile.role == 'lawyer':
            return Payment.objects.filter(case__lawyer=user)
        return Payment.objects.none()

    @action(detail=True, methods=['post'], permission_classes=[IsClient])
    def create_payment_intent(self, request, pk=None):
        """Create a Stripe payment intent"""
        payment = get_object_or_404(Payment, pk=pk)

        if payment.case.client != request.user:
            return Response(
                {'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),  # Amount in cents
                currency='inr',
                metadata={'payment_id': payment.id, 'case_number': payment.case.case_number}
            )
            payment.stripe_payment_intent_id = intent.id
            payment.save()
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            })
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def confirm_payment(self, request, pk=None):
        """Confirm payment after Stripe processing"""
        payment = get_object_or_404(Payment, pk=pk)

        try:
            intent = stripe.PaymentIntent.retrieve(payment.stripe_payment_intent_id)
            
            if intent.status == 'succeeded':
                payment.status = 'completed'
                payment.paid_at = timezone.now()
                payment.case.registration_fee_paid = True
                payment.case.save()
                payment.save()
                return Response({'message': 'Payment confirmed successfully'})
            else:
                return Response(
                    {'error': 'Payment not completed'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except stripe.error.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
