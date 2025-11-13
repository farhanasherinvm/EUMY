from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeacherAttendanceViewSet, LeaveRequestViewSet,AdminAttendanceViewSet

router = DefaultRouter()
router.register(r'leave-requests', LeaveRequestViewSet)
router.register(r'attendance', TeacherAttendanceViewSet, basename='attendance')
router.register(r'admin/attendance', AdminAttendanceViewSet, basename='attendance-admin')
urlpatterns = [
    # ... your existing SignupView, VerifyOTPView, LoginView paths ...
    path('/', include(router.urls)), 
]