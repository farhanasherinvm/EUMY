from django.db import models
from django.conf import settings
# from .models import User  <- Assuming User is defined elsewhere or imported via settings
from cloudinary_storage.storage import MediaCloudinaryStorage
class AttendanceRecord(models.Model):
    # Link to the Teacher/User who is punching in
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Links directly to your custom User model
        on_delete=models.CASCADE,
        related_name='attendance_records'
    )
    # Time of the punch-in (auto-set on creation)
    punch_in_time = models.DateTimeField(auto_now_add=True)
    # Optional punch-out time
    punch_out_time = models.DateTimeField(null=True, blank=True)
    # The uploaded selfie image
    punch_in_selfie = models.ImageField(
        upload_to='attendance_selfies/%Y/%m/%d/',default="", storage=MediaCloudinaryStorage(),
        help_text='Selfie taken at the time of punch-in.'
    )
    working_duration = models.DurationField(null=True, blank=True)
    # Optional: You might want to track duration
    # duration = models.DurationField(null=True, blank=True)

    def __str__(self):
        return f"{self.teacher.email} punched in at {self.punch_in_time.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-punch_in_time']
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"
# staff_app/models.py
from django.db import models

class LeaveRequest(models.Model):
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='leave_requests'
    )

    LEAVE_TYPES = [
        ('ANNUAL', 'Annual Leave'),
        ('SICK', 'Sick Leave'),
        ('CASUAL', 'Casual Leave'),
        ('OTHER', 'Other'),
    ]
    leave_type = models.CharField(
        max_length=15,
        choices=LEAVE_TYPES,
        default='CASUAL'
    )

    start_date = models.DateField()
    end_date = models.DateField()
    duration_days = models.PositiveSmallIntegerField(null=True, blank=True)
    reason = models.TextField(blank=False) 

    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING'
    )

    applied_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.staff.username} - {self.get_leave_type_display()} ({self.status})"

    class Meta:
        ordering = ['-applied_on']