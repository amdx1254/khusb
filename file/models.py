from django.db import models
from django.conf import settings
from django.utils import timezone
import mimetypes


class File(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='files', on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name='files', on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=200)
    modified = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    size = models.BigIntegerField(default=0)
    is_directory = models.BooleanField(default=False)
    type = models.CharField(max_length=200, blank=True, null=True)
    path = models.CharField(max_length=50000)

    def __str__(self):
        return self.path

    def set_type(self):
        types, _ = mimetypes.guess_type(self.name)
        self.type = types

    def get_all_children(self, include_self=True):
        r = []
        if include_self:
            r.append(self)
        for c in File.objects.filter(parent=self):
            _r = c.get_all_children(include_self=True)
            if 0 < len(_r):
                r.extend(_r)
        return r