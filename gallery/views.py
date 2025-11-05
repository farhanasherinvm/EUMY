from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import GalleryImage
from .serializers import GalleryImageSerializer

# Create your views here.



class GalleryListCreateView(APIView):
    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsAdminUser()]

    def get(self, request):
        images = GalleryImage.objects.all()
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


