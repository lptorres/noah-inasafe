"""

layer_manager/forms.py

A form for logged-in users to be able to upload their vector-type shapefiles.
The custom ModelForm is implemented here to be able to perform certain
validation on the user's upload before accepting and saving to the db.

"""


import collections
import os
import zipfile

from django import forms
from layer_manager.models import Layer


class LayerUploadForm(forms.ModelForm):
    """
    The custom ModelForm
    """
    def __init__(self, *args, **kwargs):
        super(LayerUploadForm, self).__init__(*args, **kwargs)
        
    def clean(self):
        """
        Override the clean method in order to validate if the user:
        1) Actually uploaded a file
        2) Uploaded a .zip file
        3) Uploaded a .zip file containing the mandatory file types
        4) Uploaded a .zip file with no extra files
        """
        cleaned_data = super(LayerUploadForm, self).clean()    

        #First check if the user uploaded a file (any)
        try:
            shapefile = cleaned_data['shapefile']
        except:
            raise forms.ValidationError("Error! You did not upload a zip file!")
        
        #Now check if the user uploaded a zip file
        if shapefile.name[-4:] != '.zip':
            raise forms.ValidationError("""Error! You did not upload a zip
                file!""")
            
        zip = zipfile.ZipFile(shapefile)
        
        #Check if the zip file is empty
        if len(zip.namelist()) == 0:
            raise forms.ValidationError("""Error! You uploaded an empty
                zip file!""")
       
        #Count the number of files per file type
        count = collections.Counter()
        for filename in zip.namelist():
            ext = os.path.splitext(filename)[1]
            count[ext] += 1
                
       #Raise an error if the zip does not contain the required file types
        required = ['.shp', '.shx', '.dbf']
        for ext in required:
            if count[ext] == 0:
                msg = "Error! The zip file does not contain a %s file." % ext
                raise forms.ValidationError(msg)
        
        #Raise an error if the zip contains more than 1 file per file type
        for ext in count:
            if count[ext] > 1:
                msg = "Error! Cannot have more than 1 %s file." % ext
                raise forms.ValidationError(msg)

        return cleaned_data

    class Meta:
        model = Layer
