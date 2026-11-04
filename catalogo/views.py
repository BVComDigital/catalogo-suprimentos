from django.shortcuts import render,redirect
from .models import Produto, Categoria
from .forms import ProdutoForm

def lista_produtos(request):
   produtos = Produto.objects.order_by('categoria__nome')

   return render(request, 'catalogo/lista_produtos.html', {'produtos':produtos})

def cadastrar_produto(request): # request: representa a requisição enviada pelo navegador
   if request.method == "POST": # verifica se o usuário enviou dados pelo formulário
      form = ProdutoForm(request.POST, request.FILES)
      # request.POST: contém os dados dos campos. request.FILES: contém arquivos enviados, como imagens.
      if form.is_valid():
         form.save()
         return redirect('lista_produtos')
   else:
      form = ProdutoForm() # cria um formulário vazio para exibição inicial.

   return render(request, 'catalogo/cadastrar_produtos.html', {'form': form})


