from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import*
from .serializers import*



class CourseListCreate(APIView):

    def get(self, request):
        courses = Course.objects.all().order_by('-created_at')
        serializer = CourseSerializer(courses, many=True)
        return Response({
            "Success": True,
            "message": "Courses fetched successfully",
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Success": True,
                "message": "Course created successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_201_CREATED)
        return Response({
            "Success": False,
            "message": "Validation error",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class CourseUpdateDelete(APIView):

    def put(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Course not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseSerializer(course, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Success": True,
                "message": "Course updated successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_200_OK)

        return Response({
            "Success": False,
            "message": "Validation error",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Course not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        course.delete()
        return Response({
            "Success": True,
            "message": "Course deleted successfully",
            "data": None,
            "errors": None
        }, status=status.HTTP_200_OK)

class SubCourseListCreate(APIView):

    def post(self, request, course_id):
        serializer = SubCourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(course_id=course_id)
            return Response({
                "Success": True,
                "message": "Subcourse created successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_201_CREATED)

        return Response({
            "Success": False,
            "message": "Validation error",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)



class SubCourseUpdateDelete(APIView):

    def put(self, request, sub_id):
        try:
            sub = SubCourse.objects.get(id=sub_id)
        except SubCourse.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Subcourse not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = SubCourseSerializer(sub, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "Success": True,
                "message": "Subcourse updated successfully",
                "data": serializer.data,
                "errors": None
            }, status=status.HTTP_200_OK)
        return Response({
            "Success": False,
            "message": "Validation error",
            "data": None,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, sub_id):
        try:
            sub = SubCourse.objects.get(id=sub_id)
        except SubCourse.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Subcourse not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        sub.delete()
        return Response({
            "Success": True,
            "message": "Subcourse deleted successfully",
            "data": None,
            "errors": None
        }, status=status.HTTP_200_OK)


class Courseget(APIView):

    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({
                "Success": False,
                "message": "Course not found",
                "data": None,
                "errors": None
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CourseSerializer(course)
        return Response({
            "Success": True,
            "message": "Course fetched successfully",
            "data": serializer.data,
            "errors": None
        }, status=status.HTTP_200_OK)
