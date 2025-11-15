from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('', include('web.urls')),
    path('admin/', admin.site.urls),
    path('api/auth/', include('auth0.urls')),
    path('api/votes/', include('votes.urls')),
    path('api/users/', include('users.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/categories/', include('categories.urls')),

    # === OPENAPI SCHEMA ===
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # === SWAGGER UI ===
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # === REDOC UI (Alternative) ===
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
