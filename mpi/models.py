from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .validators import validate_file_document


def document_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'documents/user_{0}/{1}'.format(instance.user.id, filename)


class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50, unique=True)
    date_created = models.DateTimeField(default=timezone.now)
    file = models.FileField(upload_to=document_directory_path, validators=[validate_file_document])

    def __str__(self):
        return self.name
