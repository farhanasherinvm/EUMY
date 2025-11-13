from django.db import models
from cloudinary_storage.storage import MediaCloudinaryStorage
# Create your models here.


class GalleryImage(models.Model):
    image = models.ImageField(upload_to='gallery/', default="", storage=MediaCloudinaryStorage(), null=True, blank=True)


    def __str__(self):
        return str(self.image)