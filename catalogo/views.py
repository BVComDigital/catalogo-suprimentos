from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from .models import Produto, Categoria
from .forms import ProdutoForm

def home(request):
   return render(request, 'catalogo/home.html')

@login_required
@permission_required('catalogo.view_produto', raise_exception=True)
def lista_produtos(request):
   produtos = Produto.objects.order_by('categoria__nome')
   return render(request, 'catalogo/lista_produtos.html', {'produtos':produtos})

@login_required
@permission_required('catalogo.add_produto', raise_exception=True) # raise => 403 (acesso proibido)
def cadastrar_produto(request): # request: representa a requisição enviada pelo navegador
   if request.method == "POST": # verifica se o usuário enviou dados pelo formulário
      form = ProdutoForm(request.POST, request.FILES)
      # request.POST: contém os dados dos campos. request.FILES: contém arquivos enviados, como imagens.
      if form.is_valid():
         produto = form.save(commit=False) 
         produto.cadastrado_por = request.user 
         produto.save()


         # form.save(commit=False): prepara o objeto sem gravá-lo.
         # produto.cadastrado_por = request.user: identifica o responsável.
         # produto.save(): grava o produto com essa informação.
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