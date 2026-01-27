from flask import Blueprint, render_template, request, flash, redirect
from flask_login import login_required, current_user
from grupo_andrade.procuracao.funcao_ia import ler_pdf, leito_nota_fiscal_ia
from grupo_andrade.models import User


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
        despachante = User.query.filter(User.id == current_user.despachante).first()
        print(despachante)
        if not despachante:
            flash("Selecione um despachante ", "info")
            return redirect(request.url)
        if 'documento' not in request.files:
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        file = request.files['documento']
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                texto_saida = ler_pdf(file)
                
                if "nota fiscal" in texto_saida.lower():
                    resultado_estruturado = leito_nota_fiscal_ia(texto=texto_saida)
                    print(resultado_estruturado)
                else:
                    flash('Selecione uma nota fiscal para criar a procuraçao', 'info')
                    return redirect(request.url)
            except:
                flash('Selecione uma nota fiscal para criar a procuraçao', 'info')
                return redirect(request.url)            
            return render_template('procuracao/procuracao_pronta.html',
                                 modelo='veiculos_novos',
                                 titulo=resultado_estruturado.produto.chassi,
                                 dados=resultado_estruturado, despachante=despachante)    
    return render_template("procuracao/form_veiculos_novos.html")