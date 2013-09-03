import zipfile
import os
import errno
import glob
from datetime import datetime, timedelta

from django.core.urlresolvers import reverse
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.query import QuerySet
from django.dispatch import receiver
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.gis.gdal import DataSource
from django.template.defaultfilters import slugify
from subprocess import call


class OverwriteStorage(FileSystemStorage):

    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

def zip_validator(file):
        #First check if the user uploaded a file (any)
        if not (file):
            raise ValidationError("Error! You did not upload a balls file!")
        
        #Now check if the user uploaded a zip file

        if file[-4:] != '.zip':
            raise ValidationError("""Error! You did not upload a zip
                file!""")
            
        zip = zipfile.ZipFile(file)
        
        #Check if the zip file is empty
        if len(zip.namelist()) == 0:
            raise ValidationError("""Error! You uploaded an empty
                zip file!""")
       
       #Raise an error if the zip does not contain the required file types
        required = ['.shp', '.shx', '.dbf']
        for ext in required:
            if count[ext] == 0:
                msg = "Error! The zip file does not contain a %s file." % ext
                raise ValidationError(msg)
       
        #Count the number of files per file type
        count = collections.Counter()
        for filename in zip.namelist():
            name, ext = os.path.splitext('*')
            count[ext] += 1
        
        #Raise an error if the zip contains more than 1 file per file type
        for ext in count:
            if count[ext] > 1:
                msg = "Error! Cannot have more than 1 %s file." % ext
                raise ValidationError(msg)   

class Layer(models.Model):
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
    Post process the uploaded layer
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

    # Check if it is vector or raster
    # if it has a .shp file, it is vector :)
    os.chdir(zip_out)
    shapefiles = glob.glob('*.shp')

    if len(shapefiles) > 0:
        # this means it is a vector

        # FIXME(This is a very weak way to get the shapefile)
        shapefile = shapefiles[0]

        # Use ogr to inspect the file and get the bounding box
        dse = DataSource(shapefile)
        instance.bbox = ",".join(["%s" % x for x in dse[0].extent.tuple])

        #Create GeoJSON file
        output = os.path.join(zip_out, 'geometry.json')
        call(['ogr2ogr', '-f', 'GeoJSON', output, shapefile])
