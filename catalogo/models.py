from django.db import models

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

   def __str__(self):
      return self.nome
   
