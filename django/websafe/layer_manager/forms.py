#layer_manager/forms.py
import os
import zipfile
import collections

from django import forms
from .models import Layer

class LayerUploadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(LayerUploadForm, self).__init__(*args, **kwargs)
        
    def clean(self):
    
        cleaned_data = super(LayerUploadForm, self).clean()    
        shapefile = cleaned_data.get("shapefile")
        print cleaned_data['name']
        #First check if the user uploaded a file (any)
        if not (cleaned_data['shapefile']):
            raise forms.ValidationError("Error! You did not upload a zip file!")
        
        #Now check if the user uploaded a zip file
        print shapefile
        print shapefile[-4:]
        if shapefile[-4:] != '.zip':
            raise forms.ValidationError("""Error! You did not upload a zip
                file!""")
            
        zip = zipfile.ZipFile(shapefile)
        
        #Check if the zip file is empty
        if len(zip.namelist()) == 0:
            raise forms.ValidationError("""Error! You uploaded an empty
                zip file!""")
       
       #Raise an error if the zip does not contain the required file types
        required = ['.shp', '.shx', '.dbf']
        for ext in required:
            if count[ext] == 0:
                msg = "Error! The zip file does not contain a %s file." % ext
                raise forms.ValidationError(msg)
       
        #Count the number of files per file type
        count = collections.Counter()
        for filename in zip.namelist():
            name, ext = os.path.splitext('*')
            count[ext] += 1
        
        #Raise an error if the zip contains more than 1 file per file type
        for ext in count:
            if count[ext] > 1:
                msg = "Error! Cannot have more than 1 %s file." % ext
                raise forms.ValidationError(msg)


            
        return cleaned_data

    class Meta:
        model = Layer
