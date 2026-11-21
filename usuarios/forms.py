from django import forms 
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.db import transaction



Usuario = get_user_model()

class CadastroUsuarioForm(UserCreationForm):
   grupo = forms.ModelChoiceField(
      queryset=Group.objects.filter(name__in=['Gerente', 'Funcionario']),
      label='Perfil de acesso'
   )

   class Meta(UserCreationForm.Meta):
      fields = ('username', 'password1', 'password2', 'grupo')

   def save(self, commit=True):
      with transaction.atomic():
         usuario = super().save(commit=False)

         if commit:
            usuario.save()
            self.save_m2m()

      return usuario

   def _save_m2m(self):
    super()._save_m2m()

    self.instance.groups.add(
        self.cleaned_data['grupo']
    )




class EditarUsuarioForm(forms.ModelForm):

   grupo = forms.ModelChoiceField(
      queryset=Group.objects.filter(name__in=['Gerente', 'Funcionario']),
      label='Perfil de Acesso'
   )

   ativo = forms.BooleanField(
      required=False,
      label='Usuário ativo'
   )

   class Meta:
      model = Usuario
      fields = ['username', 'first_name', 'last_name', 'email',  'grupo', 'ativo']

   
   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)

      if self.instance.pk: # recupera o grupo atual do usuário
         grupo = self.instance.groups.filter(
            name__in=['Gerente', 'Funcionario']
         ).first()

         self.fields['ativo'].initial = self.instance.is_active # preenche os formulários com os dados do usuário

         if grupo:
            self.fields['grupo'].initial = grupo


   def save(self, commit= True):
      usuario = super().save(commit=False) #prepara os dados pessoais
      usuario.is_active = self.cleaned_data['ativo'] #atualiza a situação da conta

      if commit:
         with transaction.atomic():
            usuario.save()
            self.save_m2m()

      return usuario #devolve o objeto atualizado

   def _save_m2m(self):
      super()._save_m2m()

      self.instance.groups.set([
         self.cleaned_data['grupo']
      ])


   