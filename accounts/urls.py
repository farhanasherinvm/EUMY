from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import (SignupView, VerifyOTPView, LoginView,TeamListCreateView, TeamDetailView,ReviewListCreateView, ReviewDetailView,
    StudentListCreateView, StudentDetailView,
    ExportStudentsCSV, ExportStudentsExcel, ExportStudentsPDF,ImageViewSet,ForgotPasswordView, ResetPasswordView, ChangePasswordView,ResendOTPView
)

router = DefaultRouter()
router.register(r'images', ImageViewSet, basename='image')
urlpatterns = [
    path('', include(router.urls)),
    path("signup/", SignupView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("login/", LoginView.as_view()),
    path('forgot-password/', ForgotPasswordView.as_view()),
    path('reset-password/', ResetPasswordView.as_view()),
    path('change-password/', ChangePasswordView.as_view()),
    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),

    path('team/', TeamListCreateView.as_view(), name='team-list-create'),
    path('team/<int:id>/', TeamDetailView.as_view(), name='team-detail'),
    path('reviews/', ReviewListCreateView.as_view(), name='review-list-create'),
    path('reviews/<int:id>/', ReviewDetailView.as_view(), name='review-detail'),
    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<int:id>/', StudentDetailView.as_view(), name='student-detail'),
    path('students/export/csv/', ExportStudentsCSV.as_view(), name='export-students-csv'),
    path('students/export/excel/', ExportStudentsExcel.as_view(), name='export-students-excel'),
    path('students/export/pdf/', ExportStudentsPDF.as_view(), name='export-students-pdf'),
]
