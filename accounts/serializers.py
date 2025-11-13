from rest_framework import serializers
from .models import User
from django.contrib.auth import authenticate
import random, datetime
from django.utils import timezone
from django.core.mail import send_mail
import random
from .models import TeamMember
from .models import Review
from .models import Student

from .models import Image

from django.utils.crypto import get_random_string


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["fname", "lname", "email", "phone_number", "password", "confirm_password"]

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        otp = str(random.randint(100000, 999999))

        user = User.objects.create_user(
            email=validated_data["email"],
            fname=validated_data["fname"],
            lname=validated_data["lname"],
            password=validated_data["password"]
        )
        user.phone_number = validated_data.get("phone_number", None)
        user.otp = otp
        user.otp_created_at = datetime.datetime.now()
        user.is_active = False
        user.save()

        # Send OTP to email (console backend or real email if configured)
        send_mail(
            subject="Your OTP Verification Code",
            message=f"Hello {user.fname}, your OTP is {otp}",
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            recipient_list=[user.email],
            fail_silently=False
        )
        return user


class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"], otp=data["otp"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")

        user.is_active = True
        user.otp = None
        user.save()
        return data


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(email=data["email"], password=data["password"])
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        if not user.is_active:
            raise serializers.ValidationError("Please verify your account first")
        return user



class TeamMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamMember
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    # Combine first and last name from the user model
    user_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'user', 'user_name', 'title', 'description', 'rating', 'created_at']
        read_only_fields = ['user', 'created_at']

    def get_user_name(self, obj):
        # Assuming your CustomUser model has 'fname' and 'lname' fields
        return f"{obj.user.fname} {obj.user.lname}".strip()



class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'course', 'fee_details', 'status', 'date_of_joining']


from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'title','image', 'uploaded_by', 'uploaded_at']
        read_only_fields = ['uploaded_by', 'uploaded_at']

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user found with this email.")
        return value

    def create(self, validated_data):
        """
        Called when .save() is used in the view.
        """
        email = validated_data['email']
        user = User.objects.get(email=email)

        otp = get_random_string(length=6, allowed_chars='1234567890')
        user.otp = otp
        user.otp_created_at = timezone.now()
        user.save()

        send_mail(
            subject="Password Reset OTP",
            message=f"Hello {user.fname},\n\nYour OTP for password reset is: {otp}",
            from_email="zecserbusiness@gmail.com",
            recipient_list=[email],
            fail_silently=False,
        )
        return user


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")

        try:
            user = User.objects.get(email=data["email"], otp=data["otp"])
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP or email")

        return data

    def save(self):
        user = User.objects.get(email=self.validated_data["email"])
        user.set_password(self.validated_data["new_password"])
        user.otp = None
        user.save()
        return user
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = self.context["request"].user
        if not user.check_password(data["old_password"]):
            raise serializers.ValidationError("Old password is incorrect")
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def save(self):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user


