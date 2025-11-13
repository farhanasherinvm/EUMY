from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,PermissionsMixin
from django.utils import timezone
from django.conf import settings
from datetime import date
from cloudinary_storage.storage import MediaCloudinaryStorage

class UserManager(BaseUserManager):
    def create_user(self, email, fname, lname, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, fname=fname, lname=lname)
        user.set_password(password)
        user.save(using=self._db)
        return user

    # def create_superuser(self, email, fname, lname, password=None):
    #     user = self.create_user(email, fname, lname, password)
    #     user.is_admin = True
    #     user.is_active = True
    #     user.save(using=self._db)
    #     return user
    def create_superuser(self, email, fname, lname, password=None):
        user = self.create_user(email, fname, lname, password)
        # Add is_superuser = True as well if PermissionsMixin is used
        user.is_superuser = True 
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user

# class User(AbstractBaseUser):
#     fname = models.CharField(max_length=100)
#     lname = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)
#     phone_number = models.CharField(max_length=15, null=True, blank=True)

#     is_active = models.BooleanField(default=False)
#     is_admin = models.BooleanField(default=False)
    
#     otp = models.CharField(max_length=6, blank=True, null=True)
#     otp_created_at = models.DateTimeField(null=True, blank=True)

#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ["fname", "lname"]

#     objects = UserManager()

#     def __str__(self):
#         return self.email

#     @property
#     def is_staff(self):
#         return self.is_admin

# ---------------------------------------------------------------------
# USER MODEL - ADDED PermissionsMixin
# ---------------------------------------------------------------------
class User(AbstractBaseUser, PermissionsMixin): # <-- CHANGE THIS LINE
    fname = models.CharField(max_length=100)
    lname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    is_active = models.BooleanField(default=False)
    # is_admin will now act as the superuser/staff check
    is_admin = models.BooleanField(default=False) 
    #is_staff = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fname", "lname"]

    objects = UserManager()

    def __str__(self):
        return self.email

    # --- DJANGO ADMIN/PERMISSION METHODS/PROPERTIES ---
    
    # 1. is_staff (Required for Admin Login)
    # The @property is fine, but the Django Admin often expects a boolean field 
    # named 'is_staff' or a method/property that works like a field. 
    # Your definition is correct:
    @property
    def is_staff(self):
        return self.is_admin

    # 2. is_superuser (Required by PermissionsMixin, but needs to be mapped to your custom field)
    # PermissionsMixin requires a boolean field named 'is_superuser'. 
    # Since you use 'is_admin', we define a property for 'is_superuser' 
    # or rename 'is_admin' to 'is_superuser' and update the manager.
    
    # Easiest way: Let is_admin handle superuser checks.
    @property
    def is_superuser(self):
        return self.is_admin # Maps superuser to your existing is_admin field
    
    # 3. has_perm (Required for Admin)
    def has_perm(self, perm, obj=None):
        return self.is_admin # All admins have all permissions
    
    # 4. has_module_perms (Required for Admin)
    def has_module_perms(self, app_label):
        return self.is_admin # All admins can view all app modules
# ---------------------------------------------------------------------
class TeamMember(models.Model):
    photo = models.ImageField(upload_to='team_photos/', default="", storage=MediaCloudinaryStorage(), null=True, blank=True)
    name = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    batches = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    date_of_joining = models.DateField(auto_now_add=True)
    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    rating = models.PositiveIntegerField(default=1)  # 1–5 stars
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.rating})"


class Student(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('fee_assigned', 'Fee Assigned'),
    ]

    name = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    fee_details = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_of_joining = models.DateField(default=date.today)

    def __str__(self):
        return self.name


class Image(models.Model):
    title = models.CharField(max_length=100, default="Untitled")
    image = models.ImageField(upload_to="uploads/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
