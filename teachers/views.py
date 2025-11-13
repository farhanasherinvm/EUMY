from django.shortcuts import render
from rest_framework import viewsets
from .serializers import AttendanceDisplaySerializer
# Create your views here.
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import AttendanceRecord
from .serializers import PunchInSerializer, PunchOutSerializer,AttendanceDisplaySerializer
from datetime import date

# Custom Permission Check (Same logic as before)
class IsManagerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow anyone to read (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow only managers (superuser or staff) to perform write actions
        return request.user and (request.user.is_superuser or request.user.is_staff)

# Use GenericViewSet since we only need custom actions, not default CRUD actions (list, retrieve, etc.)
class TeacherAttendanceViewSet(viewsets.GenericViewSet):
    # Only authenticated users (teachers) can use this API
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'punch_in':
            return PunchInSerializer
        # Use the display serializer for listing and retrieving 
        # (and for the final punch-out response)
        return AttendanceDisplaySerializer
    
    def get_queryset(self):
        # Ensure a teacher can only manage their own attendance records
        # request.user is the authenticated User object (the Teacher)
        return AttendanceRecord.objects.filter(teacher=self.request.user)
    # 1. New: List all attendance records for the teacher
    def list(self, request):
    #     queryset = self.get_queryset().filter(punch_out_time__isnull=False) # Only display complete records
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)
        queryset = self.get_queryset() 
        
        # You may want to order them by most recent first
        # This is often handled by the Meta class in the model, but specifying it here is safer:
        queryset = queryset.order_by('-punch_in_time') 

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    # POST /api/attendance/punch-in/
    @action(detail=False, methods=['post'], url_path='punch-in')
    def punch_in(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # 1. Check for an active, un-punched-out record for today
        already_punched_in = self.get_queryset().filter(
            punch_in_time__date=date.today(),
            punch_out_time__isnull=True
        ).exists()
        
        if already_punched_in:
            return Response(
                {"detail": "You are already punched in for today."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # # 2. Proceed with the punch-in
        # # Data must be sent as 'multipart/form-data' with a file for 'punch_in_selfie'
        # serializer = PunchInSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        
        # Save the record, linking it to the current authenticated user (the teacher)
        record = serializer.save(teacher=request.user)
        
        # We can return the full, saved data using the serializer
        return Response(
            {"detail": "Punch-in successful!",
             "status": "PUNCHED_IN",
             "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    # POST /api/attendance/{pk}/punch-out/
    @action(detail=True, methods=['post'], url_path='punch-out')
    def punch_out(self, request, pk=None):
        # 1. Get the specific attendance record for the current user
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        
        # 2. Check if the record is already punched out
        if instance.punch_out_time:
             return Response(
                {"detail": "This record is already punched out."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # 3. Use the PunchOutSerializer to update the record (sets punch_out_time)
        # We pass an empty dict for data since the time is set in the serializer's update method
        update_serializer = PunchOutSerializer(instance, data={}, partial=True)
        update_serializer.is_valid(raise_exception=True)
        updated_instance = update_serializer.save()

        # Re-serialize the full object to return complete details if needed
        # Use the AttendanceDisplaySerializer to return the formatted working hours
        response_serializer = AttendanceDisplaySerializer(updated_instance)
        
        return Response(
            {"detail": "Punch-out successful!", "data": response_serializer.data},
            status=status.HTTP_200_OK
        )
# teachers/views.py (Add this new class)


# NOTE: Make sure IsManagerOrReadOnly is imported or defined here
# from staff_app.views import IsManagerOrReadOnly # You might need this import!

# Assuming IsManagerOrReadOnly is available in this file or imported
# If not, you must copy/import it.
from rest_framework import viewsets, permissions, status
from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 1000
from datetime import timedelta
class AdminAttendanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Admin/Manager to view ALL attendance records.
    It inherits from ReadOnlyModelViewSet as admin only needs to list/retrieve, not create/update.
    """
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceDisplaySerializer
    # Use the permission class you defined for managers
    permission_classes = [permissions.IsAuthenticated, IsManagerOrReadOnly] 
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        """Returns all attendance records for manager view."""
        # We also filter for punch_out_time__isnull=False if we only want *complete* records,
        # but for an admin view, it's often better to see *all* records.
        return AttendanceRecord.objects.all().order_by('-punch_in_time')
    
    @action(detail=False, methods=['get'], url_path='punched-in-today')
    def punched_in_today(self, request):
        """Lists ALL attendance records created for the current local day (both punched-in and punched-out)."""
        
        # Get the current time, localized to TIME_ZONE='Asia/Kolkata'
        now_local = timezone.localtime(timezone.now()) 
        
        # Define the start and end of the current local day (e.g., Nov 13, 00:00:00 to Nov 14, 00:00:00)
        start_of_day = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        # Convert local times back to UTC for the database query
        start_utc = timezone.make_aware(start_of_day.replace(tzinfo=None), timezone.get_current_timezone())
        end_utc = timezone.make_aware(end_of_day.replace(tzinfo=None), timezone.get_current_timezone())

        queryset = self.get_queryset().filter(
            # 🛑 REMOVED: punch_out_time__isnull=True 🛑
            
            # Filter for records created within today's 24-hour range
            punch_in_time__gte=start_utc, 
            punch_in_time__lt=end_utc
        ).order_by('punch_in_time') # Optional: order by punch-in time

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
# staff_app/views.py
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import LeaveRequest
from .serializers import LeaveRequestSerializer, AdminLeaveStatusSerializer
from django.shortcuts import get_object_or_404

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated] # Requires login for all actions

    def get_serializer_class(self):
        """Use a different serializer for admin actions"""
        # When accessing the custom 'status' action, use the specialized serializer
        if self.action == 'update_status':
            return AdminLeaveStatusSerializer
        return LeaveRequestSerializer

    def get_queryset(self):
        """
        Staff: See only their own requests.
        Manager: See all requests.
        """
        if self.request.user.is_superuser or self.request.user.is_staff:
            return LeaveRequest.objects.all().order_by('-applied_on')
        
        # Regular staff member
        return LeaveRequest.objects.filter(staff=self.request.user).order_by('-applied_on')

    # def perform_create(self, serializer):
    #     """Auto-set the staff member to the logged-in user."""
    #     serializer.save(staff=self.request.user)
    def perform_create(self, serializer):
        # Get the validated dates from the serializer data
        start_date = serializer.validated_data['start_date']
        end_date = serializer.validated_data['end_date']
        
        # Calculate the duration (End date - Start date + 1 day)
        # The +1 ensures the start and end days are both counted
        duration = (end_date - start_date).days + 1
        
        # Save the request, including the calculated duration
        serializer.save(staff=self.request.user, duration_days=duration)
    # -----------------------------------------------------------------
    # ADMIN ACTION: Update Status
    # This replaces the POST form handling for approval/rejection.
    # Endpoint: /api/leave-requests/{pk}/update_status/
    # -----------------------------------------------------------------
    @action(detail=True, methods=['patch'], permission_classes=[IsManagerOrReadOnly])
    def update_status(self, request, pk=None):
        leave_request = self.get_object()
        
        # Check if the requested status change is valid
        new_status = request.data.get('status')
        if new_status not in ['APPROVED', 'REJECTED']:
            return Response(
                {"error": "Invalid status value. Must be 'APPROVED' or 'REJECTED'."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave_request.status = new_status
        leave_request.save()

        # Respond with the updated object details
        serializer = LeaveRequestSerializer(leave_request)
        return Response(serializer.data, status=status.HTTP_200_OK)