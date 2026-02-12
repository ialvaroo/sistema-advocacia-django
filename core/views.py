from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from docxtpl import DocxTemplate
import io

# Importando Modelos e Formulários
from .models import Cliente, ModeloDocumento, Documento
from .forms import ClienteForm
from financeiro.models import Honorario

# ========================================================
# 1. HOME (DASHBOARD) E AUTENTICAÇÃO
# ========================================================

def home(request):
    if not request.user.is_authenticated:
        form_login = AuthenticationForm()
        return render(request, 'home.html', {'form_login': form_login})
    
    total_clientes = Cliente.objects.count()
    total_docs = Documento.objects.count()
    
    total_receber = Honorario.objects.filter(status='PEN').aggregate(Sum('valor'))['valor__sum'] or 0
    total_recebido = Honorario.objects.filter(status='PAG').aggregate(Sum('valor'))['valor__sum'] or 0
    
    ultimos_docs = Documento.objects.all().order_by('-data_geracao')[:5]

    return render(request, 'home.html', {
        'total_clientes': total_clientes,
        'total_docs': total_docs,
        'total_receber': total_receber,
        'total_recebido': total_recebido,
        'ultimos_docs': ultimos_docs
    })

def cadastro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/cadastro.html', {'form': form})

# ========================================================
# 2. GESTÃO DE CLIENTES
# ========================================================

@login_required
def lista_clientes(request):
    # Removi a duplicata e mantive a separação por ativos/inativos
    clientes_ativos = Cliente.objects.filter(ativo=True).order_by('nome_completo')
    clientes_inativos = Cliente.objects.filter(ativo=False).order_by('nome_completo')
    return render(request, 'core/lista_clientes.html', {
        'clientes_ativos': clientes_ativos, 
        'clientes_inativos': clientes_inativos
    })

@login_required
def novo_cliente(request):
    # Melhorei a lógica de POST para garantir a validação
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_clientes')
        else:
            # Se houver erro, ele imprime no terminal para você ver
            print(form.errors)
    else:
        form = ClienteForm()
    return render(request, 'core/form_cliente.html', {'form': form})

@login_required
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, id=id)
    form = ClienteForm(request.POST or None, instance=cliente)
    if form.is_valid():
        form.save()
        return redirect('lista_clientes')
    return render(request, 'core/form_cliente.html', {'form': form})

# ========================================================
# 3. GESTÃO DE DOCUMENTOS
# ========================================================

@login_required
def lista_documentos(request):
    documentos = Documento.objects.all().order_by('-data_geracao')
    return render(request, 'core/lista_documentos.html', {'documentos': documentos})

@login_required
def selecionar_modelo(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    modelos = ModeloDocumento.objects.all()
    return render(request, 'core/selecionar_modelo.html', {
        'cliente': cliente,
        'modelos': modelos
    })

@login_required
def gerar_documento(request, cliente_id, modelo_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    modelo_db = get_object_or_404(ModeloDocumento, id=modelo_id)
    
    doc = DocxTemplate(modelo_db.arquivo_template.path)
    
    # Lógica de Gênero
    sufixo = 'a' if cliente.sexo == 'F' else 'o'
    
    # Mapeamento do contexto atualizado com os novos campos
    contexto = {
        'nome': cliente.nome_completo,
        'nacionalidade': f"brasileir{sufixo}",
        'estado_civil': cliente.get_estado_civil_display().lower(),
        'deficiente_tag': ", deficiente" if cliente.eh_deficiente else "",
        'nascido_tag': f"nascid{sufixo}",
        'data_nasc': cliente.data_nascimento.strftime("%d/%m/%Y") if cliente.data_nascimento else "XX/XX/XXXX",
        'cpf': cliente.cpf_cnpj,
        'rg': cliente.rg,
        'orgao': cliente.orgao_expeditor,
        'rua': cliente.endereco,
        'num': cliente.numero,
        'bairro': cliente.bairro,
        'cidade': cliente.cidade,
        'cep': cliente.cep,
        'telefone': cliente.contato,
        'profissao': cliente.profissao,
    }
    
    doc.render(contexto)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    Documento.objects.create(
        cliente=cliente,
        modelo=modelo_db,
        tipo=modelo_db.titulo,
        criado_por=request.user
    )

    filename = f"{cliente.nome_completo}_{modelo_db.titulo}.docx"
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response