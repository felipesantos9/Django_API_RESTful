from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication


schema_view = get_schema_view(
    openapi.Info(
    title="API E-commerce",
      default_version='v1',
      description="Documentação da API RESTful de E-commerce",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="felipessantos2004@gmail.com"),
      license=openapi.License(name="Licença de Uso"),
    ),
    public=True,
    permission_classes=(AllowAny,),  
    authentication_classes=(JWTAuthentication,),  
)

# URLs da aplicação
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api_app.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
