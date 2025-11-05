from django.urls import path
from .views import *

urlpatterns = [
    path('gallery/', GalleryListCreateView.as_view(), name='gallery-list-create'),
    path('gallery/<int:id>/', GalleryDetailView.as_view(), name='gallery-detail'),
]
