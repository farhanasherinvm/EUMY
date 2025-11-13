from rest_framework import serializers
from django.utils import timezone
from .models import AttendanceRecord
from django.conf import settings
from django.contrib.auth import get_user_model
class StaffDetailSerializer(serializers.ModelSerializer):
    class Meta:
        # model = settings.AUTH_USER_MODEL
        model = get_user_model()
        # Expose the specific fields you want from the User model
        fields = ['fname', 'lname', 'email']

class PunchInSerializer(serializers.ModelSerializer):
    #punch_in_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S")
    #punch_in_time = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S %Z", read_only=True)
    class Meta:
        model = AttendanceRecord
        
        # Client only sends the selfie file
        fields = ('id', 'punch_in_selfie', 'punch_in_time','punch_out_time') 
        # ID and time are handled by the model/view, making them read-only for input
        read_only_fields = ('id','punch_in_time','punch_out_time')
# teachers/serializers.py (Continued)

class PunchOutSerializer(serializers.ModelSerializer):
    # ... (Your existing code for Meta and update method) ...
    class Meta:
        model = AttendanceRecord
        fields = ('id', 'punch_out_time')
        read_only_fields = ('id', 'punch_out_time') # Keep these read_only for security

    def update(self, instance, validated_data):
        instance.punch_out_time = timezone.now()
        
        if instance.punch_in_time:
            duration = instance.punch_out_time - instance.punch_in_time
            instance.working_duration = duration  
            
        instance.save()
        return instance
from rest_framework import serializers
from django.utils import timezone

from .models import AttendanceRecord

class AttendanceDisplaySerializer(serializers.ModelSerializer):
    # This remains the same logic for formatting duration
    working_hours = serializers.SerializerMethodField()
    teacher = StaffDetailSerializer(read_only=True)
    # 🌟 NEW: Direct access to the username
    teacher_username = serializers.CharField(source='teacher.username', read_only=True)
    class Meta:
        model = AttendanceRecord
        # All fields required for display, but they are all read-only
        fields = ('id','teacher', 'teacher_username', 'punch_in_selfie', 'punch_in_time', 'punch_out_time', 'working_hours',)
        read_only_fields = fields # IMPORTANT: Mark all fields as read-only for output
        
    def get_working_hours(self, obj):
        if obj.working_duration is None:
            return "N/A (Punched In)"
        
        total_seconds = int(obj.working_duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        
        return f"{hours}h {minutes}m"
# staff_app/serializers.py
from rest_framework import serializers
from .models import LeaveRequest
from datetime import date

class LeaveRequestSerializer(serializers.ModelSerializer):
    # Read-only field to show the staff member's username
    staff = StaffDetailSerializer(read_only=True)
    staff_username = serializers.CharField(source='staff.username', read_only=True)
    duration_days = serializers.SerializerMethodField()
    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'staff', 'staff_username', 'leave_type', 
            'start_date', 'end_date', 'reason', 'status','duration_days', 'applied_on'
        ]
        # These fields should NOT be set by the staff member
        read_only_fields = ['status', 'staff', 'applied_on','duration_days'] 

    def validate(self, data):
        """Custom validation for dates (used for POST/PUT/PATCH)"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # Check 1: No past dates
        if start_date and start_date < date.today():
            raise serializers.ValidationError({"start_date": "Leave cannot be applied for a past date."})

        # Check 2: Duration validity
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError("End date cannot be before the start date.")
        
        return data
    # Define the method to calculate the duration
    def get_duration_days(self, obj: LeaveRequest) -> int:
        """Calculates the total number of days, inclusive of start and end dates."""
        
        # Ensure both dates are present and are date objects
        if obj.start_date and obj.end_date:
            # Calculation: (End Date - Start Date) + 1 day
            # The +1 is crucial to count both the start and end days
            duration = (obj.end_date - obj.start_date).days + 1
            return duration
        return 0 # Return 0 or None if dates are missing

# Serializer for Admin to ONLY change the status
class AdminLeaveStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['id', 'status']
        read_only_fields = ['id']