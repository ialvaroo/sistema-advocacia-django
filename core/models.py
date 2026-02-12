from django.db import models
from django.contrib.auth.models import User


class Cliente(models.Model):

    SEXO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino')
    ]


    ESTADO_CIVIL_CHOICES = [
        ('S', 'Solteiro(a)'),
        ('C', 'Casado(a)'),
        ('D', 'Divorciado(a)'),
        ('V', 'Viúvo(a)'),
    ]

    #Dados Pessoais 
    nome_completo = models.CharField(max_length=255)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default='M', verbose_name="Sexo")
    nacionalidade = models.CharField(max_length=50, default='Brasileira(o)')
    estado_civil = models.CharField(max_length=1, choices=ESTADO_CIVIL_CHOICES)
    eh_deficiente = models.BooleanField(default=False, verbose_name="É Pessoa com Deficiência?")

    #Documentos  e Nascimento 
    cpf_cnpj = models.CharField(max_length=20, unique=True, verbose_name="CPF/CNPJ")
    rg = models.CharField(max_length=20, blank=True, null=True, verbose_name="RG")
    orgao_expeditor = models.CharField(max_length=20, blank=True, null=True, verbose_name="Órgão Expeditor")
    data_nascimento = models.DateField(null=True, blank=True, verbose_name="Data de Nascimento")

    #Endereço
    endereco = models.CharField(max_length=255, verbose_name="Rua / Logradouro") # Mudou de TextField para CharField
    numero = models.CharField(max_length=10, verbose_name="Número")
    bairro = models.CharField(max_length=100, default='')
    cidade = models.CharField(max_length=100, default='')
    cep = models.CharField(max_length=10, verbose_name="CEP")

    profissao = models.CharField(max_length=100)
    contato = models.CharField(max_length=100, help_text="Email ou Telefone")
    
    # O campo novo entra aqui, fora da lista de choices
    ativo = models.BooleanField(default=True, verbose_name="Cliente Ativo?")
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nome_completo

class ModeloDocumento(models.Model):
    titulo = models.CharField(max_length=100)
    descricao = models.TextField(blank=True)
    arquivo_template = models.FileField(upload_to='templates_docs/', help_text="Arquivo .docx base com as tags {{nome}}, etc.")
    
    def __str__(self):
        return self.titulo

class Documento(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='documentos')
    modelo = models.ForeignKey(ModeloDocumento, on_delete=models.SET_NULL, null=True, blank=True)
    tipo = models.CharField(max_length=50)
    arquivo_gerado = models.FileField(upload_to='documentos_gerados/')
    data_geracao = models.DateTimeField(auto_now_add=True)
    criado_por = models.ForeignKey(User, on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.tipo} - {self.cliente.nome_completo}"