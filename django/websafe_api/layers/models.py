"""

layer_manager/models.py

This file contains the models for the layer_manager app, and receivers for
post-processing.

"""



import errno
import glob
import os
import shutil
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

from smart_selects.db_fields import ChainedForeignKey



class OverwriteStorage(FileSystemStorage):
    """
    A FileSystemStorage type that the FileField in the Layer model will use. This
    custom FileSystemStorage type will overwrite any file with the same filename.
    """
    def get_available_name(self, name):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

        

class Category(models.Model):
    """
    A model to represent the different categories for Layers
    """
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return self.name
    

class Subcategory(models.Model):
    """
    A model to represent the different subcategories for Layers
    """
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category)
    
    def __unicode__(self):
        return self.name
    
        
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
    
    layer_category = models.ForeignKey(Category)
    layer_subcategory = ChainedForeignKey(Subcategory,
        chained_field='layer_category', chained_model_field='category')
    owner = models.ForeignKey('auth.User', related_name='layers')
    date_added = models.DateTimeField(editable=False)
    slug = models.SlugField(editable=False)
    
    def save(self, *args, **kwargs):
        """
        Save method for the Layer model
        """
        if self.date_added:
            pass
        else:
            now = datetime.utcnow() +timedelta(hours=8)    
            self.date_added = now
            to_slug = self.name + now.strftime('%Y%m%d%H%M%S')
            self.slug = slugify(to_slug)        
    
    def __unicode__(self):
        return self.name
        
    def get_absolute_url(self):
        return reverse("layers:detail", kwargs={"slug": self.slug})
        
    class Meta:
        ordering = ('name')
        
        
        
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

            
           
def delete_directory(path):
    """
    A method to delete a directory and all of its subdirectories and contents.
    """
    try:
        shutil.rmtree(path)
    except:
        print 'Something went wrong'

        
"""        
@receiver(models.signals.pre_save, sender=Layer)
def post_process(sender, instance, *args, **kwargs):
    """
    Post process the uploaded layer.
    Assign a date & time to the instance's 'date_added' attribute
    Create a slug for the instance
    Get the bounding box information
    Create a .keywords file
    """
    
    #Because auto_now_add adds the date and time AFTER saving the model,
    #manually add the date and time and create a slug
    if instance.date_added: 
        print 'Editing your model...'
    else:
        now = datetime.utcnow() +timedelta(hours=8)    
        instance.date_added = now
        to_slug = instance.name + now.strftime('%Y%m%d%H%M%S')
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
    projectionfile = glob.glob('*.prj')
    if len(shapefiles) > 0:
        """
        We can be sure that there is only one shapefile in this list since
        we already validated that in the clean method of LayerUploadForm
        """
        shapefile = shapefiles[0]

        # Use ogr to inspect the file and get the bounding box
        dse = DataSource(shapefile)
        instance.bbox = ",".join(["%s" % x for x in dse[0].extent.tuple])
        
        # Create GeoJSON file using the EPSG:4326 projection
        output = os.path.join(zip_out, 'geometry.json')
        call(['ogr2ogr', '-f', 'GeoJSON', '-a_srs', 'EPSG:4326', output, shapefile])
        
    # Open a new file with using the same filename as the .shp file
    filename = os.path.splitext(shapefile)[0] + '.keywords'
    f = open(filename, 'w')
    category = 'category: %s' % instance.layer_category
    subcategory = 'subcategory: %s' % instance.layer_subcategory
    f.write(category + '\n')
    f.write(subcategory)
    f.close()
""" 

 
@receiver(models.signals.pre_delete, sender=Layer)   
def layer_delete(sender, instance, *args, **kwargs):
    """
    A receiver for deleting the assiociated zip file and the directory
    containing the extracted contents before deleting a model instance.
    """
    
    #This is the directory containing the contents of the original zip file
    layer_folder = os.path.join(settings.MEDIA_ROOT, 'layers', instance.slug)
    #This is the path of the original zip file
    original_upload = os.path.join(settings.MEDIA_ROOT, instance.shapefile.name)
    #Delete the directory with the extracted contents
    delete_directory(layer_folder)
    #Delete the original upload
    os.remove(original_upload)