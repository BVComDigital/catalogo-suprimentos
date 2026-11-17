from .models import HistoricoProduto, CAMPOS_AUDITAVEIS


def registrar_historico_produto(produto, usuario, valores_anteriores=None):
   for campo, descrição in CAMPOS_AUDITAVEIS:

      valor_atual = getattr(produto,campo)

      if campo == 'categoria':
         valor_atual = valor_atual.nome

      valor_anterior = None

      if valores_anteriores is not None:
         valor_anterior = valores_anteriores[campo]

         if valor_anterior == valor_atual:
            continue

      HistoricoProduto.objects.create(
         produto=produto,
         produto_nome=produto.nome,
         usuario=usuario,
         campo=campo,
         valor_anterior=str(valor_anterior) if valor_anterior is not None else None,
         valor_novo=str(valor_atual)
      )
