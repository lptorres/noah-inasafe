
from django.contrib.auth.models import User
from django.forms import widgets

from rest_framework import serializers

from layer_manager.models import Layer


class LayerSerializer(serializers.ModelSerializer):
    owner = serializers.Field(source='owner.username')
    
    class Meta:
        model = Layer
        fields = ('slug', 'name', 'description', 'bbox', 'shapefile',
                  'layer_category', 'layer_subcategory', 'owner',
                  'date_added')

class UserSerializer(serializers.ModelSerializer):
    layers = serializers.HyperlinkedRelatedField(many=True,
        view_name='layer-detail')
        
    class Meta:
        model = User
        fields = ('username', 'layers')