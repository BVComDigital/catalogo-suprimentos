from typing import Any

from django.contrib import admin
from django.db.models import F, DecimalField, ExpressionWrapper
from django.db.models.functions import NullIf
from django.http import HttpRequest
from .models import Categoria, Produto

admin.site.register(Categoria)

@admin.register(Produto) #registra o modelo usando a classe personalizada
class ProdutoAdmin(admin.ModelAdmin):
   list_display = (
      'id',
      'nome',
      'categoria',
      'preco',
      'custo',
      'exibir_lucro', # pode usar o nome da propriedade lucro_bruto
      'exibir_margem',
      'estoque',
      'cadastrado_por',
      'alterado_por',
      
   ) # list_display aceita não apenas campos do banco de dados, mas também métodos e propriedades.

   readonly_fields = ('cadastrado_por', 'alterado_por',)

   @admin.display(description="Lucro bruto (R$)", ordering='lucro_calculado') # personaliza os títulos e a apresentação dos métodos epropriedades
   def exibir_lucro(self, obj): # obj representa o produto que está sendo exibido naquela linha
      return f'R$ {obj.lucro_bruto:.2f}' # obj.lucro_bruto acessa a propriedade que criamos no modelo

   @admin.display(description='Margem bruta (%)', ordering="margem_calculada")
   def exibir_margem(self, obj):
      return f'{obj.margem_bruta:.2f} %'

   def get_queryset(self, request):
      queryset = super().get_queryset(request)

      return queryset.annotate(
         lucro_calculado=ExpressionWrapper(
            F('preco') - F('custo'),
            output_field=DecimalField(max_digits=10, decimal_places=2)            
         ),
         margem_calculada=ExpressionWrapper(
            ((F('preco') - F('custo')) / NullIf(F('preco'), 0)) * 100, 
            output_field=DecimalField(max_digits=10, decimal_places=2)
         )
         )

   def save_model(self, request, obj, form, change): # Salvaalterações feita no admin
      if change:
         obj.alterado_por = request.user
      else:
         obj.cadastrado_por = request.user
      return super().save_model(request, obj, form, change)
         
