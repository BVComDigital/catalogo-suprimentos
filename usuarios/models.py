from django.db import models

class PerfilAcesso(models.Model):

   class Meta:

      permissions = [
         ('gerenciar_usuarios', 'Pode gerenciar usuários')
      ]
