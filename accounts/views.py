from django.shortcuts import render
from datetime import datetime
# Create your views here.
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import SignupSerializer, VerifyOtpSerializer, LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import TeamMember
from .serializers import TeamMemberSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Review
from .serializers import ReviewSerializer
from openpyxl import Workbook
from .pagination import TeamMemberPagination
from .serializers import ForgotPasswordSerializer
from .models import Profile
from .serializers import ProfileSerializer

from django.db.models import Q
from .models import Student
from .serializers import StudentSerializer
import csv
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from .serializers import ResetPasswordSerializer
from .serializers import ChangePasswordSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from .models import User
import random

class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP sent to email"}, status=201)
        return Response(serializer.errors, status=400)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if serializer.is_valid():
            return Response({"message": "Account verified successfully"})
        return Response(serializer.errors, status=400)

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            })
        return Response(serializer.errors, status=400)

class TeamListCreateView(APIView):
    pagination_class = TeamMemberPagination
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]  # POST → admin only

    def get(self, request):
        members = TeamMember.objects.all().order_by('id')

         # --- Search filters ---
        search = request.query_params.get('search', None)
        from_date = request.query_params.get('from_date', None)
        end_date = request.query_params.get('end_date', None)

        if search:
            members = members.filter(
                Q(name__icontains=search)
                | Q(qualification__icontains=search)
                | Q(batches__icontains=search)
                | Q(role__icontains=search)
            )

        # --- Date range filter ---
        if from_date and end_date:
            members = members.filter(date_of_joining__range=[from_date, end_date])
        elif from_date:
            members = members.filter(date_of_joining__gte=from_date)
        elif end_date:
            members = members.filter(date_of_joining__lte=end_date)
        # 🌟 PAGINATION LOGIC 🌟
        paginator = self.pagination_class()
        
        # 1. Paginate the queryset
        page = paginator.paginate_queryset(members, request, view=self)
        
        if page is not None:
            # 2. Serialize the paginated data (the current page)
            serializer = TeamMemberSerializer(page, many=True)
            # 3. Return the standard paginated response (includes links, count, etc.)
            return paginator.get_paginated_response(serializer.data)
        # serializer = TeamMemberSerializer(members, many=True)
        # return Response(serializer.data)
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data)
    def post(self, request):
        serializer = TeamMemberSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TeamDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]  # PUT, DELETE → admin only

    def get(self, request, id):
        try:
            member = TeamMember.objects.get(id=id)
            serializer = TeamMemberSerializer(member)
            return Response(serializer.data)
        except TeamMember.DoesNotExist:
            return Response({'error': 'Team member not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, id):
        try:
            member = TeamMember.objects.get(id=id)
            serializer = TeamMemberSerializer(member, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TeamMember.DoesNotExist:
            return Response({'error': 'Team member not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        try:
            member = TeamMember.objects.get(id=id)
            member.delete()
            return Response({'message': 'Team member deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except TeamMember.DoesNotExist:
            return Response({'error': 'Team member not found'}, status=status.HTTP_404_NOT_FOUND)



class ReviewListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]  # anyone can list
        return [IsAuthenticated()]  # only logged-in user can add

    def get(self, request):
        reviews = Review.objects.all().order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response({
            "Success": True,
            "message": "Reviews fetched successfully",
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({
                "Success": True,
                "message": "Review added successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_201_CREATED)
        return Response({
            "Success": False,
            "message": "Validation error",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ReviewDetailView(APIView):
    def get_permissions(self):
        if self.request.method in ['DELETE']:
            return [IsAuthenticated()]  # user/admin can delete
        return [IsAuthenticated()]  # for edit (PUT)

    def put(self, request, id):
        try:
            review = Review.objects.get(id=id, user=request.user)  # user can only edit own review
        except Review.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Review not found or permission denied",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ReviewSerializer(review, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Success": True,
                "message": "Review updated successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_200_OK)
        return Response({
            "Success": False,
            "message": "Validation error",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            review = Review.objects.get(id=id)
        except Review.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Review not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        # user can delete own review, admin can delete any
        if review.user != request.user and not request.user.is_staff:
            return Response({
                "Success": False,
                "message": "Permission denied",
                "data": None,
                "errors": None
            }, status=status.HTTP_403_FORBIDDEN)

        review.delete()
        return Response({
            "Success": True,
            "message": "Review deleted successfully",
            "data": None,
            "errors": None
        }, status=status.HTTP_204_NO_CONTENT)




class StudentListCreateView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        search = request.query_params.get('search', None)
        status_param = request.query_params.get('status', None)
        course = request.query_params.get('course', None)
        from_date = request.query_params.get('from_date', None)
        to_date = request.query_params.get('to_date', None)

        queryset = Student.objects.all()

        # --- Search by name or course ---
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(course__icontains=search)
            )

        # --- Filter by status ---
        if status_param:
            queryset = queryset.filter(status__iexact=status_param)

        # --- Filter by course ---
        if course:
            queryset = queryset.filter(course__icontains=course)

        # --- Filter by date range ---
        try:
            if from_date:
                from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
                queryset = queryset.filter(date_of_joining__gte=from_date)
            if to_date:
                to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
                queryset = queryset.filter(date_of_joining__lte=to_date)
        except ValueError:
            return Response({
                "Success": False,
                "message": "Invalid date format. Use YYYY-MM-DD.",
                "data": None,
                "errors": None
            }, status=status.HTTP_400_BAD_REQUEST)

        # --- Serialize ---
        serializer = StudentSerializer(queryset, many=True)
        return Response({
            "Success": True,
            "message": "Students fetched successfully",
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = StudentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Success": True,
                "message": "Student added successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_201_CREATED)
        return Response({
            "Success": False,
            "message": "Validation error",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
class StudentDetailView(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request, id):
        try:
            student = Student.objects.get(id=id)
        except Student.DoesNotExist:
            return Response({"Success": False, "message": "Student not found"}, status=404)

        serializer = StudentSerializer(student, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Success": True,
                "message": "Student updated successfully",
                "data": serializer.data,
                "errors": None
            })
        return Response({
            "Success": False,
            "message": "Validation error",
            "data": None,
            "errors": serializer.errors
        }, status=400)

    def delete(self, request, id):
        try:
            student = Student.objects.get(id=id)
        except Student.DoesNotExist:
            return Response({"Success": False, "message": "Student not found"}, status=404)

        student.delete()
        return Response({
            "Success": True,
            "message": "Student deleted successfully",
            "data": None,
            "errors": None
        })


# ---------- EXPORT VIEWS ---------- #

class ExportStudentsCSV(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'

        writer = csv.writer(response)
        writer.writerow(['Name', 'Course', 'Fee Details', 'Status', 'Date of Joining'])

        for student in Student.objects.all():
            writer.writerow([student.name, student.course, student.fee_details, student.status, student.date_of_joining])

        return response


class ExportStudentsExcel(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        wb = Workbook()
        ws = wb.active
        ws.title = "Students"

        ws.append(['Name', 'Course', 'Fee Details', 'Status', 'Date of Joining'])

        for student in Student.objects.all():
            ws.append([student.name, student.course, student.fee_details, student.status, str(student.date_of_joining)])

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = 'attachment; filename="students.xlsx"'
        wb.save(response)
        return response


class ExportStudentsPDF(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="students.pdf"'

        pdf = SimpleDocTemplate(response, pagesize=letter)
        styles = getSampleStyleSheet()

        data = [['Name', 'Course', 'Fee Details', 'Status', 'Date of Joining']]
        for s in Student.objects.all():
            data.append([s.name, s.course, s.fee_details, s.status, str(s.date_of_joining)])

        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))

        pdf.build([Paragraph("Student Report", styles['Heading1']), table])
        return response


# views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Image
from .serializers import ImageSerializer
from .permissions import IsAdminOrReadOnly

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all().order_by('-uploaded_at')
    serializer_class = ImageSerializer
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)

    def create(self, request, *args, **kwargs):
        """
        Allow multiple image uploads in one request.
        """
        images = request.FILES.getlist('images')  # multiple files
        title = request.data.get('title', 'Untitled')

        if not images:
            return Response({'error': 'No images provided.'}, status=status.HTTP_400_BAD_REQUEST)

        image_objects = []
        for img in images:
            image_obj = Image.objects.create(
                title=title,
                image=img,
                uploaded_by=request.user
            )
            image_objects.append(image_obj)

        serializer = self.get_serializer(image_objects, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ForgotPasswordView(APIView):
    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "OTP sent to your email"}, status=200)
        return Response(serializer.errors, status=400)


class ResetPasswordView(APIView):
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset successful"}, status=200)
        return Response(serializer.errors, status=400)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password changed successfully"}, status=200)
        return Response(serializer.errors, status=400)




class ResendOTPView(APIView):
    def post(self, request):
        email = request.data.get("email")

        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User with this email does not exist"}, status=status.HTTP_404_NOT_FOUND)

          # ✅ Check if OTP is still valid (5 minutes)
        if user.otp_created_at and timezone.now() - user.otp_created_at < timedelta(minutes=5):
            remaining = 300 - int((timezone.now() - user.otp_created_at).seconds)
            return Response(
                {"error": f"OTP already sent. Please wait {remaining} seconds before requesting a new one."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # ✅ Generate new OTP
        otp = str(random.randint(100000, 999999))
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        # ✅ Send OTP via email
        send_mail(
            subject="Your OTP Code",
            message=f"Your OTP is {otp}. It will expire in 5 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "OTP resent successfully"}, status=status.HTTP_200_OK)

# accounts/views.py

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, created = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=200)

    def put(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)
