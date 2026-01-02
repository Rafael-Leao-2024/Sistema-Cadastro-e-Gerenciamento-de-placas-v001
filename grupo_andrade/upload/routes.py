from flask import Blueprint, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from flask import current_app
from flask_login import login_required, current_user
from PyPDF2 import PdfReader
import os

from botocore.exceptions import NoCredentialsError

from grupo_andrade.models import UploadFile, Placa, Boleto, Taxa
from grupo_andrade.main import db
from grupo_andrade.placas.routes import injetar_notificacao
from grupo_andrade.upload.funcoes_aws import enviar_arquivo_s3, ver_arquivo
from dotenv import load_dotenv
from grupo_andrade.upload.funcoesIA import ler_pdf, gerador_saida_estruturada
from grupo_andrade.upload.funcao_taxa_ia import extrator_taxa_ia
from grupo_andrade.atividade.services import registrar_atividade

load_dotenv()

documentos_bp  = Blueprint('documentos', __name__, template_folder='templates', url_prefix="/documentos/")

@documentos_bp.context_processor
def inject_notificacoes_documentos():
    return injetar_notificacao()


ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documentos_bp.route("/upload/<name>")
@login_required
def download_file(name):
    return ver_arquivo(filename=name)



@documentos_bp.route('/upload-anexo/<id_placa>', methods=['GET', 'POST'])
@login_required
def upload_file_anexo(id_placa):
    placa = Placa.query.filter(Placa.id == id_placa).first()
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Selecione um ou mais arquivos', category='info')
            return redirect(url_for('documentos.upload_file_anexo', id_placa=placa.id))
        files = request.files.getlist('file')
        if files[0].filename == '':
            flash('Selecione um ou mais arquivos', category='info')
            return redirect(url_for('documentos.upload_file_anexo', id_placa=placa.id))   
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                
                try:
                    saida_texto = ler_pdf(file)
                    reader = PdfReader(file)
                    for page in reader.pages:
                        saida_texto_boleto = page.extract_text()
                    
                        if "valor cobrado" in saida_texto_boleto.lower():
                            taxas_estruturadas = extrator_taxa_ia(saida_texto_boleto)
                            # taxas_estruturadas.taxas = deduplicar_taxas(taxas_estruturadas.taxas)

                            if not taxas_estruturadas.taxas:
                                raise ValueError("Nenhuma taxa válida encontrada")

                            boleto_db = Boleto(id_placa=id_placa, usuario_id=current_user.id)
                            db.session.add(boleto_db)
                            db.session.commit()
                            db.session.refresh(boleto_db)

                            print(taxas_estruturadas)

                            for taxa in taxas_estruturadas.taxas:
                                taxa_db = Taxa(
                                    descricao=taxa.descricao, 
                                    valor=taxa.valor, 
                                    id_boleto=boleto_db.id
                                )
                                db.session.add(taxa_db)
                            db.session.commit()


                    if "senatran" in saida_texto.lower():
                        saida_estruturada = gerador_saida_estruturada(saida_texto)
                        print(saida_estruturada.veiculo)
                        placa.placa = saida_estruturada.veiculo.placa
                        placa.chassi = saida_estruturada.veiculo.chassi
                        placa.renavan = saida_estruturada.veiculo.codigo_renavam
                        placa.crlv = saida_estruturada.veiculo.numero_do_crv
                        placa.nome_proprietario = saida_estruturada.proprietario.nome
                    
                    # RESET do cursor do arquivo para o início antes de enviar para AWS
                    file.seek(0)
                    
                except Exception as e:
                    print(f"Erro na leitura do PDF: {e}")
                    # Mesmo com erro na leitura, tenta fazer upload do arquivo
                    file.seek(0)  # Reset do cursor antes de continuar
                    continue
                
                # armazenamento AWS
                try:
                    enviar_arquivo_s3(file=file, filename=filename)
                    flash(f'Arquivo {filename} enviado com sucesso ', category="success")
                except NoCredentialsError:
                    flash('Credenciais invalidas', 'info')
                    return redirect(url_for('documentos.upload_file_anexo', id_placa=placa.id))
                except Exception as e:
                    flash(f'Erro no upload {str(e)}', 'info')
                    return redirect(url_for('documentos.upload_file_anexo', id_placa=placa.id))
                                
                file_db = UploadFile(filename=filename, id_usuario=current_user.id, id_placa=placa.id)
                db.session.add(file_db)
                db.session.commit()
            else:
                flash('apenas arquivos PDFs sao permitidos', 'info')
                return redirect(url_for('documentos.upload_file_anexo', id_placa=placa.id))
                
        return redirect(url_for('documentos.download_anexos', id_placa=id_placa))           
    return render_template('upload/muitos_file.html', title="muitos uploads", placa=placa)




@documentos_bp.route('/download/<id_placa>')
@login_required
def download_anexos(id_placa):
    placa = Placa.query.filter(Placa.id == id_placa).first()
    if not placa:
        flash(f'Placa nao encontrada com id {id_placa}.', 'info')
        return redirect(url_for('placas.gerenciamento_pedidos'))

    if current_user.id != placa.id_user and not current_user.is_admin:
        flash('Voce nao tem permissao para acessar esses arquivos.', 'info')
        return redirect(url_for('placas.gerenciamento_pedidos'))

    files = UploadFile.query.filter(UploadFile.id_placa == id_placa).all()
    return render_template('upload/download.html', files=files, title="todos Downloads", placa=placa)


@documentos_bp.route('/upload/<id_file>/delete', methods=['GET', 'POST'])
@login_required
def delete_file(id_file):
    file = UploadFile.query.filter(UploadFile.id == id_file).first()
    
    placa = Placa.query.filter(Placa.id == file.id_placa).first()
    if request.method == 'POST':
        file_record = UploadFile.query.get(id_file)
        if file_record:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_record.filename)
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.delete(file_record)
        db.session.commit()

        registrar_atividade(
            usuario_id=current_user.id,
            acao="DELETE",
            descricao=f"{current_user.username.upper()} deletou o arquivo {file_record.filename} da placa {placa.placa.upper()}"
        )

        flash(f'Arquivo {file_record.filename} deletado com sucesso', category='success')
        return redirect(url_for('documentos.download_anexos', id_placa=placa.id))
    return render_template('upload/delete.html', file=file, title="Confirmar Exclusão", placa=placa)