from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from .models import Produto, Categoria
from .forms import ProdutoForm

def home(request):
   return render(request, 'catalogo/home.html')

@login_required
@permission_required('catalogo.view_produto', raise_exception=True)
def lista_produtos(request):

   produtos = Produto.objects.order_by('categoria__nome')

   busca = request.GET.get('busca')

   categorias = Categoria.objects.all()

   categoria_id = request.GET.get('categoria')

   preco_min = request.GET.get('preco_min')

   preco_max = request.GET.get('preco_max')

   estoque_filtro = request.GET.get('estoque')

   ordenacao = request.GET.get('ordenacao')

   if busca:
      produtos = produtos.filter(nome__icontains=busca)

   if categoria_id:
      produtos = produtos.filter(categoria_id=categoria_id) #Django cria automaticamente um atributo categoria_id para armazenar a chave estrangeira associada ao produto

   if preco_min:
      produtos = produtos.filter(preco__gte=preco_min)

   if preco_max:
    produtos = produtos.filter(preco__lte=preco_max)

    #Estoque
   if estoque_filtro == 'sem_estoque':
      produtos = produtos.filter(estoque=0)
   elif estoque_filtro == 'baixo':
      produtos = produtos.filter(estoque__gt=0, estoque__lte=5)
   elif estoque_filtro == 'disponível':
      produtos = produtos.filter(estoque__gt=5)

   if ordenacao in ['nome', '-nome', 'preco', '-preco', 'estoque', '-estoque']:
      produtos = produtos.order_by(ordenacao)

   paginator = Paginator(produtos, 10)
   numero_pagina = request.GET.get('page')
   produtos = paginator.get_page(numero_pagina)

   parametros = request.GET.copy() #cria uma cópia dos parâmetros da URL
   parametros.pop('page', None) # retira apenas o número da página anterior, os demais permanecem

   return render(
      request,
      'catalogo/lista_produtos.html',
      {'produtos':produtos, 'categorias':categorias, 'parametros':parametros.urlencode(),}
      )

@login_required
@permission_required('catalogo.view_produto', raise_exception=True)
def detalhe_produto(request, pk):
   produto = get_object_or_404(Produto, pk=pk)

   return render(request, 'catalogo/detalhe_produto.html', {'produto':produto})


@login_required
@permission_required('catalogo.add_produto', raise_exception=True) # raise => 403 (acesso proibido)
def cadastrar_produto(request): # request: representa a requisição enviada pelo navegador

   if request.method == "POST": # verifica se o usuário enviou dados pelo formulário
      form = ProdutoForm(request.POST, request.FILES)
      # request.POST: contém os dados dos campos. request.FILES: contém arquivos enviados, como imagens.
      if form.is_valid():

         produto = form.save(commit=False) # form.save(commit=False): prepara o objeto sem gravá-lo.

         produto.cadastrado_por = request.user # produto.cadastrado_por = request.user: identifica o responsável.

         produto.save()# produto.save(): grava o produto com essa informação.
         
         messages.success(request, "Produto cadastrado com sucesso!")

         return redirect('lista_produtos')
   else:
      form = ProdutoForm() # cria um formulário vazio para exibição inicial.

   return render(request, 'catalogo/cadastrar_produto.html', {'form': form})


@login_required
@permission_required('catalogo.change_produto', raise_exception=True)
def editar_produto(request, pk): 
   produto = get_object_or_404(Produto, pk=pk)

   if request.method == "POST": 
      form = ProdutoForm(request.POST, request.FILES, instance=produto)
      
      if form.is_valid():
         produto = form.save(commit=False)
         produto.alterado_por = request.user
         produto.save()
         messages.success(request, "Produto atualizado com sucesso!")
         return redirect('lista_produtos')
   else:
      form = ProdutoForm(instance=produto) 

   return render(request, 'catalogo/editar_produto.html', {'form': form, 'produto': produto})

@login_required
@permission_required('catalogo.delete_produto', raise_exception=True)
def excluir_produto(request, pk):
   produto = get_object_or_404(Produto, pk=pk)

   if request.method == 'POST':
      produto.delete()
      messages.success(request, "Produto excluído com sucesso!")
      return redirect('lista_produtos')
   messages.warning(
        request,
        f"Atenção! Você está prestes a excluir o produto {produto.nome}."
    )
   return render(request, 'catalogo/confirmar_exclusao.html', { 'produto': produto})