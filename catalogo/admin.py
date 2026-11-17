from typing import Any

from django.contrib import admin
from django.db import transaction
from django.db.models import F, DecimalField, ExpressionWrapper
from django.db.models.functions import NullIf
from django.http import HttpRequest
from .models import Categoria, Produto, HistoricoProduto
from .services import registrar_historico_produto

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

   def save_model(self, request, obj, form, change):
      valores_anteriores = None

      if change:
         produto_anterior = Produto.objects.get(pk=obj.pk)

         valores_anteriores = {
               'nome': produto_anterior.nome,
               'preco': produto_anterior.preco,
               'custo': produto_anterior.custo,
               'estoque': produto_anterior.estoque,
               'categoria': produto_anterior.categoria.nome,
         }

      if change:
         obj.alterado_por = request.user
      else:
         obj.cadastrado_por = request.user

      with transaction.atomic():
         super().save_model(request, obj, form, change)

         registrar_historico_produto(
               obj,
               request.user,
               valores_anteriores
         )

   def delete_model(self, request, obj):
    with transaction.atomic():
        HistoricoProduto.objects.create(
            produto=obj,
            produto_nome=obj.nome,
            usuario=request.user,
            campo='exclusao',
            valor_anterior=str(obj.nome),
            valor_novo='Produto excluído'
        )

        super().delete_model(request, obj)
         

@admin.register(HistoricoProduto)
class HistoricoProdutoAdmin(admin.ModelAdmin):
    list_display = (
        'produto_nome',
        'usuario',
        'data_hora',
        'campo',
        'valor_anterior',
        'valor_novo',
    )

    list_filter = ('campo', 'data_hora', 'usuario')

    search_fields = ('produto_nome', 'usuario__username')

    readonly_fields = (
        'produto',
        'produto_nome',
        'usuario',
        'data_hora',
        'campo',
        'valor_anterior',
        'valor_novo',
    )

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False