from django.urls import path
from .views import *
from django.urls import path
from .views import*

urlpatterns = [
    path('courses/', CourseListCreate.as_view()),
    path('courses/<int:course_id>/', CourseUpdateDelete.as_view()),
    path('courses/<int:course_id>/subcourses/', SubCourseListCreate.as_view()),
    path('subcourses/<int:sub_id>/', SubCourseUpdateDelete.as_view()),
    path('courses_by_id/<int:course_id>/', Courseget.as_view()),
]
