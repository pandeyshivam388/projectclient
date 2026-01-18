from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from core.views import (
    UserRegistrationView, UserProfileView, CaseRequestViewSet,
    CaseViewSet, RejectedCaseViewSet, CaseNoteViewSet, PaymentViewSet
)

router = DefaultRouter()
router.register(r'case-requests', CaseRequestViewSet, basename='case-request')
router.register(r'cases', CaseViewSet, basename='case')
router.register(r'rejected-cases', RejectedCaseViewSet, basename='rejected-case')
router.register(r'case-notes', CaseNoteViewSet, basename='case-note')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    # Authentication
    path('auth/register/', UserRegistrationView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User Profile
    path('profile/', UserProfileView.as_view(), name='user_profile'),

    # API Routes
    path('', include(router.urls)),

    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]
