from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import GalleryImage
from .serializers import GalleryImageSerializer
from .pagination import GalleryPagination
# Create your views here.

    
    

class GalleryListCreateView(APIView):
    pagination_class = GalleryPagination
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        images = GalleryImage.objects.all().order_by('id')
        # serializer = GalleryImageSerializer(images, many=True)
        # return Response(serializer.data)
        paginator = self.pagination_class()
        
        # 1. Paginate the queryset, returning only the current page's objects
        page = paginator.paginate_queryset(images, request, view=self)
        
        if page is not None:
            # 2. Serialize the current page data
            serializer = GalleryImageSerializer(page, many=True)
            # 3. Return the paginated response (includes links, count, etc.)
            return paginator.get_paginated_response(serializer.data)

        # Fallback (in case pagination fails)
        serializer = GalleryImageSerializer(images, many=True)
        return Response(serializer.data)

    def post(self, request):
        files = request.FILES.getlist('images')  
        created = []

        for file in files:
            serializer = GalleryImageSerializer(data={'image': file})
            if serializer.is_valid():
                serializer.save()
                created.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(created, status=status.HTTP_201_CREATED)
    
class GalleryDetailView(APIView):
    permission_classes = [IsAdminUser] 
    def delete(self, request, id):
        try:
            image = GalleryImage.objects.get(id=id)
            image.delete()
            return Response({'message': 'Image deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except GalleryImage.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)


