from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        # Listamos todos os novos campos aqui
        fields = [
            'nome_completo', 'sexo', 'nacionalidade', 'estado_civil', 'eh_deficiente',
            'data_nascimento', 'cpf_cnpj', 'rg', 'orgao_expeditor', 'profissao',
            'cep', 'cidade', 'bairro', 'endereco', 'numero', 
            'contato', 'ativo'
        ]
        
        widgets = {
            'nome_completo': forms.TextInput(attrs={'class': 'form-control'}),
            'cpf_cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'orgao_expeditor': forms.TextInput(attrs={'class': 'form-control'}),
            'data_nascimento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nacionalidade': forms.TextInput(attrs={'class': 'form-control'}),
            'profissao': forms.TextInput(attrs={'class': 'form-control'}),
            'contato': forms.TextInput(attrs={'class': 'form-control'}),
            'cep': forms.TextInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'bairro': forms.TextInput(attrs={'class': 'form-control'}),
            'endereco': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-select'}),
            'estado_civil': forms.Select(attrs={'class': 'form-select'}),
            'ativo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'eh_deficiente': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }