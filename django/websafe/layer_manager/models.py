"""

layer_manager/models.py

This file contains the models for the layer_manager app, and receivers for
post-processing.

"""


import errno
import glob
import os
import zipfile

from subprocess import call
from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.query import QuerySet
from django.dispatch import receiver
from django.template.defaultfilters import slugify


class OverwriteStorage(FileSystemStorage):
    """
    A FileSystemStorage type that the FileField in the Layer model will use. This
    custom FileSystemStorage type will overwrite any file with the same filename.
    """
    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

        
class Layer(models.Model):
    """
    A Layer model for abstracting a shapefile.
    """
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    bbox = models.CharField(max_length=255, null=True, blank=True)
    shapefile = models.FileField(storage=OverwriteStorage(), 
        upload_to='uploads', help_text="""Zip file containing the shapefile
        (mandatory files are: *.shp, *.shx, *.dbf)"""
    )
    layer_category = models.CharField(max_length=1, choices = (
        ('H', 'Hazard'),
        ('E', 'Exposure'),
        )
    )
    date_added = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(editable=False)
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse("layers:detail", kwargs={"slug": self.slug})
        
        
def create_folder(path):
    """
    A method to create a folder on the system for uploads.
    """
    try:
        os.makedirs(path)
    # This only works for Python > 2.5
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise


@receiver(models.signals.pre_save, sender=Layer)
def layer_handler(sender, instance, *args, **kwargs):
    """
    Post process the uploaded layer.
    Assign a date & time to the instance's 'date_added' attribute
    Create a slug for the instance
    Get the bounding box information and save it with the model
    """
    
    now = datetime.utcnow() +timedelta(hours=8)    
    to_slug = instance.name + now.strftime('%Y%m%d%H%M%S')
    instance.date_added = now
    instance.slug = slugify(to_slug)
    
    # Deletes an existing layer with the same slug name
    for layer in Layer.objects.filter(slug=instance.slug):
        layer.delete()

    # Make a folder with the slug name
    # and create a 'raw' subdirectory to hold the files
    layer_folder = os.path.join(settings.MEDIA_ROOT, 'layers', instance.slug)
    create_folder(layer_folder)
    zip_out = os.path.join(layer_folder, 'raw')
    create_folder(zip_out)

    # Iterate over the files in the zip and create them in the raw folder.
    the_zip = zipfile.ZipFile(instance.shapefile)
    for name in the_zip.namelist():
        outfile = open(os.path.join(zip_out, name), 'wb')
        outfile.write(the_zip.read(name))
        outfile.close()

    # Get the .shp file
    os.chdir(zip_out)
    shapefiles = glob.glob('*.shp')

    if len(shapefiles) > 0:
        """
        We can be sure that there is only one shapefile in this list since
        we already validated that in the clean method of LayerUploadForm
        """
        shapefile = shapefiles[0]

        # Use ogr to inspect the file and get the bounding box
        dse = DataSource(shapefile)
        instance.bbox = ",".join(["%s" % x for x in dse[0].extent.tuple])

        #Create GeoJSON file
        output = os.path.join(zip_out, 'geometry.json')
        call(['ogr2ogr', '-f', 'GeoJSON', output, shapefile])
