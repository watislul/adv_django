from django.urls import path, include 
from rest_framework.routers import DefaultRouter 
from .views import ItemViewSet, RegisterView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView 
 
router = DefaultRouter() 
router.register(r'items', ItemViewSet) 

urlpatterns = [ 
    path('', include(router.urls)), 
]
 
urlpatterns += [ 
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'), 
] 

urlpatterns += [ 
    path('register/', RegisterView.as_view(), name='register'), 
] 