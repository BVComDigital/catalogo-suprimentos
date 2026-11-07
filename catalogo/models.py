from django.db import models
from django.conf import settings

class Categoria(models.Model):
   nome = models.CharField(max_length=100)
   descricao = models.TextField(blank=True)

   def __str__(self):
      return self.nome

class Produto(models.Model):
   nome = models.CharField(max_length=150)
   descricao = models.TextField(blank=True)
   preco = models.DecimalField(max_digits=10, decimal_places=2)
   custo = models.DecimalField(max_digits=10, decimal_places=2)
   estoque = models.PositiveIntegerField(default=0)
   categoria = models.ForeignKey(
      Categoria, on_delete=models.PROTECT, related_name='produtos'
      )
   imagem = models.ImageField(upload_to="produtos/", blank=True, null=True)
   cadastrado_por = models.ForeignKey(
      settings.AUTH_USER_MODEL, # referencia o modelo de usuários do projeto
      on_delete=models.SET_NULL, # se o usuário for excluído, o produto permanece cadastrado, mas perde a referência ao usuário
      null=True,
      blank=True,
      related_name='produtos_cadastrados'
   )
   alterado_por = models.ForeignKey(
      settings.AUTH_USER_MODEL,
      on_delete=models.SET_NULL,
      null=True,
      blank=True,
      related_name="produtos_alterados"
   )

   def __str__(self):
      return self.nome

   @property
   def lucro_bruto(self):
      return self.preco - self.custo

   @property
   def margem_bruta(self):
      if self.preco == 0:
         return 0
      
      return (self.lucro_bruto / self.preco) * 100
   
