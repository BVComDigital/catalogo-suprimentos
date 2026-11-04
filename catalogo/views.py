from django.shortcuts import render
from .models import Produto, Categoria

def lista_produtos(request):
   produtos = Produto.objects.order_by('categoria__nome')

   return render(request, 'catalogo/lista_produtos.html', {'produtos':produtos})


