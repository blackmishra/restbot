from django.urls import path, include
from .views import (
    ResyListApiView,
)

urlpatterns = [
    path('api', ResyListApiView.as_view()),
]