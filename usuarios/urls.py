from django.urls import path
from .views import EntrarView, cadastrar_usuario, lista_usuarios, editar_usuario

urlpatterns = [
    path('login/', EntrarView.as_view(), name='login'),
    path('novo/', cadastrar_usuario, name='cadastrar_usuario'),
    path('lista/', lista_usuarios, name='lista_usuarios'),
    path('editar/<int:pk>/', editar_usuario, name='editar_usuario'),
]
