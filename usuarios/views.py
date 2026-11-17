from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required, permission_required
from .forms import CadastroUsuarioForm, EditarUsuarioForm



Usuario = get_user_model()



class EntrarView(LoginView):
   template_name = 'usuarios/login.html'


@login_required
@permission_required('usuarios.gerenciar_usuarios', raise_exception=True)
def cadastrar_usuario(request):
   if request.method == "POST":
      form = CadastroUsuarioForm(request.POST)

      if form.is_valid():
         form.save()
         messages.success(request, "Usuário cadastrado com sucesso!")
         return redirect('lista_usuarios')
   else:
      form = CadastroUsuarioForm()

   return render(request, 'usuarios/cadastrar_usuario.html', {'form': form})


@login_required
@permission_required('usuarios.gerenciar_usuarios', raise_exception=True)
def lista_usuarios(request):
    usuarios = Usuario.objects.filter(
        groups__name__in=['Gerente', 'Funcionario'],
        is_superuser=False,
        is_staff=False
    ).exclude(
       groups__name='Administrador local'
    ).distinct().prefetch_related('groups')

    return render(
    request,
    'usuarios/lista_usuarios.html',
    {'usuarios': usuarios}
)


@login_required
@permission_required('usuarios.gerenciar_usuarios', raise_exception=True)
def editar_usuario(request, pk):
   usuario = get_object_or_404(
      Usuario.objects.exclude(
         groups__name='Administrador local'#impede a edição de Administradores locais
      ).filter( 
      pk=pk,
      is_superuser=False, # impede que a view localize um superusuário
      is_staff=False,
      groups__name__in=['Gerente', 'Funcionario']
      ).distinct() # restrição a estes grupos
   )

   if request.method == 'POST':
      form = EditarUsuarioForm(request.POST, instance=usuario)
      # instance=usuario é fundamental: ele informa ao ModelForm qual registro existente deverá ser editado, em vez de criar um novo
      if form.is_valid():
         form.save()
         messages.success(request, 'Usuário atualizado com sucesso!')
         return redirect('lista_usuarios')
   else:
      form = EditarUsuarioForm(instance=usuario)

   return render(
      request, 'usuarios/editar_usuario.html',
      {
         'form':form,
         'usuario': usuario
      }
   )