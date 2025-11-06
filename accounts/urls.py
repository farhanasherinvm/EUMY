from django.urls import path
from .views import (SignupView, VerifyOTPView, LoginView,TeamListCreateView, TeamDetailView,ReviewListCreateView, ReviewDetailView,
    StudentListCreateView, StudentDetailView,
    ExportStudentsCSV, ExportStudentsExcel, ExportStudentsPDF)

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("login/", LoginView.as_view()),
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
