from django.db import models

# Create your models here.


class GalleryImage(models.Model):
    image = models.ImageField(upload_to='gallery/')

    def __str__(self):
        return str(self.image)