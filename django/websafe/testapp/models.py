from django.db import models
from django.core.files.storage import FileSystemStorage
from django.core.urlresolvers import reverse
class OverwriteStorage(FileSystemStorage):
    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

class TestModel(models.Model):
    name = models.CharField(max_length=255)
    shapefile = models.FileField(storage=OverwriteStorage(),
        null=True, blank=True, upload_to='uploads',
        help_text='Upload a file here'
    )
    date_added = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=255)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('my_detail', kwargs={'slug': self.slug})
