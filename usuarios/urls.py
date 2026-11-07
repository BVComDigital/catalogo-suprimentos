from django.urls import path
from .views import EntrarView

urlpatterns = [
    path('login/', EntrarView.as_view(), name='login'),
]
