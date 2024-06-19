from django.contrib import admin
from django.urls import include, path
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path("botlab/", admin.site.urls),
    path("auth/", include("accounts_engine.urls")),
    path("", include("waypoint_generator.urls")),
]

urlpatterns += staticfiles_urlpatterns()
