from rest_framework import viewsets 
from .models import Item 
from .serializers import ItemSerializer
from rest_framework.permissions import IsAuthenticated 
from .permissions import IsAdmin 
from rest_framework import generics 
from .serializers import RegisterSerializer 
from django.contrib.auth import get_user_model 
 
class ItemViewSet(viewsets.ModelViewSet): 
    queryset = Item.objects.all() 
    serializer_class = ItemSerializer 
 
    def get_permissions(self): 
        if self.request.method in ['POST', 'PUT', 'DELETE']: 
            return [IsAuthenticated(), IsAdmin()] 
        return [IsAuthenticated()] 
    

User = get_user_model() 

class RegisterView(generics.CreateAPIView): 
    queryset = User.objects.all() 
    serializer_class = RegisterSerializer 