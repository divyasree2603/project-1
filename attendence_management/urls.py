from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('attendence_app.urls')), # Link directly to the custom app paths
]