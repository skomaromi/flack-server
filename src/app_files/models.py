from django.conf import settings
from django.db import models

from .storage.ipfs_storage import InterPlanetaryFileSystemStorage


class File(models.Model):
    file = models.FileField(storage=InterPlanetaryFileSystemStorage())
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='files')

    class Meta:
        ordering = ['name']

    # TODO: do something with the ipfs hash
    # either:
    #  * define on save, or
    #  * make it a models.Manager, or ...
    #  * move to a dedicated serializer

    def __str__(self):
        return str(self.name)
