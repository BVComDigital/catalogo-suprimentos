from django import forms

class TesteProdutoForm(forms.Form):
   nome = forms.CharField(label="nome do produto", max_length=150)
   preco = forms.DecimalField(label="Preço", max_digits=10, decimal_places=2)