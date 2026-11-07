from django import forms
from .models import Produto

class TesteProdutoForm(forms.Form):
   nome = forms.CharField(label="nome do produto", max_length=150)
   preco = forms.DecimalField(label="Preço", max_digits=10, decimal_places=2)

class ProdutoForm(forms.ModelForm):
   class Meta:
      model = Produto
      fields = [
         'nome',
         'descricao',
         'preco',
         'custo',
         'estoque',
         'categoria',
         'imagem',
      ]

      widgets = {
         "descrição": forms.Textarea(
            attrs={'rows' : 3}
         )
      }

      labels = {
         'nome': 'Nome do Produtos',
         "preco": "Preço de venda (R$)",
         "custo": "Custo de aquisição (R$)",
         "estoque": "Quantidade disponível",
      }

      help_text = {
         'preco': 'Informe o preço de venda do produto.',
         'custo': 'Informe o quanto o produto custou para a clínica.'
      }

   def clean_preco(self): #executa o método durante is_valid(), permitindo validar especificamente o campo preco. is_valid(): executa a validação do formulário.
      preco = self.cleaned_data['preco']

      if preco <= 0:
         raise forms.ValidationError(
            'O preço deve ser maior que zero.'
         )
      return preco


   def clean(self): # permite validar dois ou mais campos em conjunto
      cleaned_data = super().clean() # executa a validação padrão do Django

      preco = cleaned_data.get('preco') # recupera os valores já convertidos e validados
      custo = cleaned_data.get('custo')

      if preco is not None and custo is not None:
         if preco < custo:
            raise forms.ValidationError(
               'O preço de venda não pode ser inferior ao preço de custo.'
            )
      return cleaned_data
   # essa regra será aplicada ao formulário. Ela não impede, por si só, que um produto seja cadastrado por outros meios, como pelo Django Shell
