from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_clientes, name='lista_clientes'),
    path('novo/', views.novo_cliente, name='novo_cliente'),
    path('documentos/', views.lista_documentos, name='lista_documentos'), 
    path('selecao/<int:cliente_id>/', views.selecionar_modelo, name='selecionar_modelo'),
    path('gerar_doc/<int:cliente_id>/<int:modelo_id>/', views.gerar_documento, name='gerar_documento'),
    path('editar/<int:id>/', views.editar_cliente, name='editar_cliente'),
]
