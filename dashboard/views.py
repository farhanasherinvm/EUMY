from django.shortcuts import render

# Create your views here.
# course/views.py (Add this new class)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from course.models import Course
# Assuming Course model is imported via from .models import *
# Assuming SubCourse model is imported via from .models import *

class DashboardView(APIView):
    """
    API view to provide key dashboard statistics, starting with total course count.
    Requires Admin/Staff user.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        # 1. Get the total count of all Course objects
        total_course_count = Course.objects.count()
        
        # 2. You could also get the SubCourse count
        # total_subcourse_count = SubCourse.objects.count()

        return Response({
            "Success": True,
            "message": "Dashboard statistics fetched successfully",
            "data": {
                "total_course_count": total_course_count,
                # "total_subcourse_count": total_subcourse_count, # Include if needed
            },
            "errors": None
        }, status=status.HTTP_200_OK)

# ... (rest of your CourseListCreate, CourseUpdateDelete, etc. views)