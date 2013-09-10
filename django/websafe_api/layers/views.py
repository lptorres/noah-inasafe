# Create your views here.
from layers.models import Layer
from layers.serializers import LayerSerializer, UserSerializer
from rest_framework import generics



class LayerList(generics.ListCreateAPIView):
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer
    
    
    
class LayerDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Layer.objects.all()
    serializer_class = LayerSerializer
    
    
    
class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


    
class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer