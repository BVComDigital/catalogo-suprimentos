from django.db import models
from django.db.models import Q, F
from django.conf import settings
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError 

class Categoria(models.Model):
   nome = models.CharField(max_length=100)
   descricao = models.TextField(blank=True)

   def __str__(self):
      return self.nome

class Produto(models.Model):
   nome = models.CharField(max_length=150)
   descricao = models.TextField(blank=True)
   preco = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
   custo = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
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
   

   def clean(self):
      if self.custo > self.preco:
         raise ValidationError({
            'custo': 'O custo não pode ser maior que o preço de venda.'
         })
      return super().clean()

   
   class Meta:
      constraints = [
         models.CheckConstraint(
            condition=Q(custo__lte=F('preco')),
            name='custo_menor_ou_igual_preco',
            violation_error_message='O preço de venda não pode ser inferior ao preço de custo.'
         )
      ]


CAMPOS_AUDITAVEIS = [
   ('nome', 'Nome'),
   ('preco', 'Preço'),
   ('custo', 'Custo'),
   ('estoque', 'Estoque'),
   ('categoria', 'Categoria'),
]

CAMPOS_HISTORICO = CAMPOS_AUDITAVEIS + [
    ('exclusao', 'Exclusão'),
]

class HistoricoProduto(models.Model):
   produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True, blank=True, related_name='historico')
   produto_nome = models.CharField(max_length=150)
   usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
   data_hora = models.DateTimeField(auto_now_add=True)
   campo = models.CharField(max_length=20, choices=CAMPOS_HISTORICO)
   valor_anterior = models.TextField(blank=True, null=True)
   valor_novo= models.TextField()