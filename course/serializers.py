from rest_framework import serializers
from .models import *


class SubCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCourse
        fields = ['id', 'course', 'name', 'created_at']
        read_only_fields = ['course']


class MultiSelectFieldSerializer(serializers.Field):
    """
    Custom serializer field to handle MultiSelectField correctly
    (works with JSON and form-data inputs).
    """

    def to_representation(self, value):
        # Display as list in the response
        if isinstance(value, str):
            return value.split(',') if value else []
        return list(value)

    def to_internal_value(self, data):
        # Accepts list input directly
        if isinstance(data, list):
            return data

        # Handles "online,offline" or "['online','offline']"
        if isinstance(data, str):
            data = data.strip()
            try:
                parsed = ast.literal_eval(data)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            # Fallback: comma-separated string
            return [v.strip() for v in data.split(',') if v.strip()]

        raise serializers.ValidationError("Invalid format for mode field.")


class CourseSerializer(serializers.ModelSerializer):
    subcourses = SubCourseSerializer(many=True, read_only=True)
    mode = MultiSelectFieldSerializer()  # ✅ force use of custom field

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'duration', 'fee', 'mode', 'created_at', 'subcourses']