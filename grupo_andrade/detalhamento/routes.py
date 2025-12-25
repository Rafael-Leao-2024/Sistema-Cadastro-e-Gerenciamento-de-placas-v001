from flask import Blueprint, render_template, url_for, redirect, abort, flash
from flask_login import login_required, current_user
from grupo_andrade.models import Boleto, Placa, db, Taxa
from grupo_andrade.placas.routes import injetar_notificacao
from sqlalchemy import desc
from sqlalchemy.orm import joinedload
from .form import FormularioBoleto


detalhamento = Blueprint("detalhamento", __name__, url_prefix="/detalhamento")

@detalhamento.context_processor
def inject_notifications():
    return injetar_notificacao()


@detalhamento.route("/criando-boleto-id-placa-<int:id_placa>", methods=["GET", "POST"])
@login_required
def criar_boleto(id_placa):
    from datetime import datetime
    form = FormularioBoleto()
    
    placa = Placa.query.get_or_404(id_placa)

    if form.validate_on_submit():
        # Criar o boleto
        boletodb = Boleto(id_placa=id_placa, usuario_id=current_user.id)
        db.session.add(boletodb)
        db.session.commit()
        db.session.refresh(boletodb)
        
        # Criar a taxa associada ao boleto
        taxadb = Taxa(
            descricao=form.descricao.data, 
            valor=form.valor.data, 
            id_boleto=boletodb.id
        )
        db.session.add(taxadb)
        db.session.commit()
        
        flash('Boleto criado com sucesso!', 'success')
        return redirect(url_for("detalhamento.detalhamento_debito_placa", id_placa=id_placa))
    
    return render_template("detalhamento/criar_boleto.html", form=form, id_placa=id_placa, placa=placa, now=datetime.now())


@detalhamento.route('/todos-os-boletos', methods=['GET', 'POST'])
@login_required
def detalhamento_debito():
    placas = Placa.query.options(joinedload(Placa.author))\
               .filter_by(id_user=current_user.id)\
               .order_by(desc(Placa.date_create)).all()
    return render_template('detalhamento/debitos.html', placas=placas)


@detalhamento.route('/boleto-debito-unico-placa-<int:id_placa>')
@login_required
def detalhamento_debito_placa(id_placa):
    placa = Placa.query.filter(Placa.id==id_placa).first()
    if not placa:
        return redirect(url_for("detalhamento.detalhamento_debito"))
    # Verificar permissão
    if not current_user.is_admin:
        flash("Usuario nao permitido")
        return redirect(url_for("detalhamento.detalhamento_debito"))
        
    return render_template("/detalhamento/boleto_debito_unico.html", placa=placa)


@detalhamento.route('/boleto-debito-unico-placa-<int:id_boleto>/delete')
@login_required
def deletar_boleto(id_boleto):
    if not current_user.is_admin:
        flash("Voce nao tem permissao de ADMIN")
        return redirect(url_for("detalhamento.detalhamento_debito"))
    boleto = Boleto.query.filter(Boleto.id==id_boleto).first()
    if not boleto:
        flash(f"boleto com {id_boleto} nao encontrado")
        return redirect(url_for("detalhamento.detalhamento_debito"))
    db.session.delete(boleto)
    db.session.commit()
    flash("Boleto Deletado com sucesso!")
    return redirect(url_for("detalhamento.detalhamento_debito"))

