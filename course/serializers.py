from rest_framework import serializers
from .models import *

class SubCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCourse
        fields = ['id', 'course', 'name', 'created_at']
        read_only_fields = ['course']


class CourseSerializer(serializers.ModelSerializer):
    subcourses = SubCourseSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'duration', 'fee', 'created_at', 'subcourses']

