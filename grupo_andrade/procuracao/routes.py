from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required, current_user
import os
from werkzeug.utils import secure_filename
from grupo_andrade.procuracao.funcao_ia import ler_pdf, gerador_saida_estruturada


procuracao = Blueprint("procuracao", __name__, template_folder="templates")


# Configurações para upload de arquivos
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}
UPLOAD_FOLDER = 'uploads/procuracao'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@procuracao.route("/procuracao")
@login_required
def selecionar_modelo():
    """Página inicial para seleção do modelo de procuração"""
    return render_template("procuracao/selecionar_modelo.html")


@procuracao.route("/procuracao/veiculos-novos", methods=['GET', 'POST'])
@login_required
def veiculos_novos():
    """Modelo de procuração para veículos novos"""
    if request.method == 'POST':
        # Processar upload do arquivo
        if 'documento' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        file = request.files['documento']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Aqui você salvaria o arquivo e processaria os dados
            # file.save(os.path.join(UPLOAD_FOLDER, filename))
            texto_saida = ler_pdf(file)
            resultado_estruturado = gerador_saida_estruturada(texto=texto_saida)         
            # Simulando dados processados do arquivo
            dados_processados = {
                'NOME_OUTORGANTE': resultado_estruturado.destinatario.nome_destinatario,
                'CNPJ': resultado_estruturado.destinatario.cnpj_destinatario,
                'CIDADE': resultado_estruturado.destinatario.cidade_destinatario,
                'UF': resultado_estruturado.destinatario.cidade_destinatario,
                'PLACA': 'ABC1D23',
                'RENAVAM': '123456789',
                'MARCA_MODELO': 'Fiat Argo',
                'CHASSI': '9BWZZZ377VT004251',
                'SERVICOS': 'Licenciamento e transferência'
            }
            
            return render_template('procuracao/procuracao_pronta.html',
                                 modelo='veiculos_novos',
                                 dados=resultado_estruturado)
    
    return render_template("procuracao/form_veiculos_novos.html")

@procuracao.route("/procuracao/transferencia", methods=['GET', 'POST'])
@login_required
def transferencia():
    """Modelo de procuração para transferência"""
    if request.method == 'POST':
        # Processar upload do arquivo
        if 'documento' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        file = request.files['documento']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Aqui você salvaria o arquivo e processaria os dados
            # file.save(os.path.join(UPLOAD_FOLDER, filename))
            
            # Simulando dados processados do arquivo
            dados_processados = {
                'NOME_OUTORGANTE': 'Maria Santos',
                'RG_OUTORGANTE': '7654321',
                'ORGAO_EMISSOR_OUTORGANTE': 'SSP',
                'CPF_OUTORGANTE': '987.654.321-00',
                'PLACA': 'XYZ9A87',
                'RENAVAM': '987654321',
                'MARCA_MODELO': 'Volkswagen Gol',
                'CHASSI': '9BWZZZ377VT004252',
                'SERVICOS': 'Transferência de propriedade'
            }

            
            texto_saida = ler_pdf(file)
            resultado_estruturado = gerador_saida_estruturada(texto=texto_saida)
            
            flash('Documento processado com sucesso!', 'success')
            return render_template('procuracao/procuracao_pronta.html', 
                                 modelo='transferencia',
                                 dados=resultado_estruturado)
    
    return render_template("procuracao/form_transferencia.html")

@procuracao.route("/procuracao/padrao")
@login_required
def procuracao_padrao():
    """Procuração padrão"""
    conteudo = {"conteudo": "conteudo1"}
    return render_template("procuracao/procuracao_padrao.html", context=conteudo)