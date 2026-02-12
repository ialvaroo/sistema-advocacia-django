from django.shortcuts import render, redirect, get_object_or_404 
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from docxtpl import DocxTemplate
import io
from .models import Cliente, ModeloDocumento, Documento
from .forms import ClienteForm
from financeiro.models import Honorario

# ========================================================
# 1. HOME (DASHBOARD) E AUTENTICAÇÃO
# ========================================================

def home(request):
    # Se não estiver logado, mostra tela simples
    if not request.user.is_authenticated:
        return render(request, 'home.html')
    
    # 1. Totais Simples
    total_clientes = Cliente.objects.count()
    total_docs = Documento.objects.count()
    
    # 2. Financeiro (Soma dos valores)
    total_receber = Honorario.objects.filter(status='PEN').aggregate(Sum('valor'))['valor__sum'] or 0
    total_recebido = Honorario.objects.filter(status='PAG').aggregate(Sum('valor'))['valor__sum'] or 0
    
    # 3. Últimos 5 documentos gerados
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
    clientes = Cliente.objects.all()
    return render(request, 'core/lista_clientes.html', {'clientes': clientes})
    
@login_required
def lista_clientes(request):
    clientes_ativos = Cliente.objects.filter(ativo=True).order_by('nome_completo')
    clientes_inativos = Cliente.objects.filter(ativo=False).order_by('nome_completo')
    return render(request, 'core/lista_clientes.html', {
        'clientes_ativos': clientes_ativos, 
        'clientes_inativos': clientes_inativos
    })

@login_required
def novo_cliente(request):
    form = ClienteForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_clientes')
    return render(request, 'core/form_cliente.html', {'form': form})

# FUNÇÃO DE EDITAR
@login_required
def editar_cliente(request, id):
    # Busca o cliente ou avisa se não existir
    cliente = get_object_or_404(Cliente, id=id)
    
    # Preenche o formulário com os dados existentes
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
    cliente = Cliente.objects.get(id=cliente_id)
    modelos = ModeloDocumento.objects.all()
    return render(request, 'core/selecionar_modelo.html', {
        'cliente': cliente,
        'modelos': modelos
    })

@login_required
def gerar_documento(request, cliente_id, modelo_id):
    # 1. Busca dados
    cliente = Cliente.objects.get(id=cliente_id)
    modelo_db = ModeloDocumento.objects.get(id=modelo_id)
    
    # 2. Carrega template
    doc = DocxTemplate(modelo_db.arquivo_template.path)
    
    # 3. Define contexto
    contexto = {
        'nome_completo': cliente.nome_completo,
        'cpf_cnpj': cliente.cpf_cnpj,
        'rg': cliente.rg,
        'endereco': cliente.endereco,
        'estado_civil': cliente.get_estado_civil_display(),
        'profissao': cliente.profissao,
    }
    
    # 4. Renderiza
    doc.render(contexto)
    
    # 5. Salva na memória
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    
    # 6. Salva no histórico
    Documento.objects.create(
        cliente=cliente,
        modelo=modelo_db,
        tipo=modelo_db.titulo,
        criado_por=request.user
    )

    # 7. Download
    filename = f"{cliente.nome_completo}_{modelo_db.titulo}.docx"
    response = HttpResponse(buffer.getvalue(), content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response