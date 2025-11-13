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
