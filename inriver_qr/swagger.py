from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings

schema_view = get_schema_view(
   
   
   openapi.Info(
      title="Product QR API",
      default_version='v1',
      description="API for generating QR codes for products",
      contact=openapi.Contact(email="support@example.com"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
   authentication_classes=(TokenAuthentication,),

   url= settings.BASE_API_URL,
)
