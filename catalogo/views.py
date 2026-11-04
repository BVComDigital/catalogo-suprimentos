from django.shortcuts import render,redirect, get_object_or_404
from django.contrib import messages
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
         messages.success(request, "Produto cadastrado com sucesso!")
         return redirect('lista_produtos')
   else:
      form = ProdutoForm() # cria um formulário vazio para exibição inicial.

   return render(request, 'catalogo/cadastrar_produto.html', {'form': form})


def editar_produto(request, pk): 
   produto = get_object_or_404(Produto, pk=pk)

   if request.method == "POST": 
      form = ProdutoForm(request.POST, request.FILES, instance=produto)
      
      if form.is_valid():
         form.save()
         messages.success(request, "Produto atualizado com sucesso!")
         return redirect('lista_produtos')
   else:
      form = ProdutoForm(instance=produto) 

   return render(request, 'catalogo/editar_produto.html', {'form': form, 'produto': produto})


def excluir_produto(request, pk):
   produto = get_object_or_404(Produto, pk=pk)

   if request.method == 'POST':
      produto.delete()
      messages.success(request, "Produto excluído com sucesso!")
      return redirect('lista_produtos')

   return render(request, 'catalogo/confirmar_exclusao.html', { 'produto': produto})