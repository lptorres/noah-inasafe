
from django.contrib.auth.models import User

from rest_framework import serializers
from layers.models import Layer



class LayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Layer
        fields = ('name', 'description', 'bbox', 'shapefile',
                  'layer_category', 'layer_subcategory', 'owner')
                  
                  
                  
class UserSerializer(serializers.ModelSerializer):
    layers = serializers.PrimaryKeyRelatedField(many=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'layers')