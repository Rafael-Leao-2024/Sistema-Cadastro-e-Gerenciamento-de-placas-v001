from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from grupo_andrade.models import User, db
 

despachante = Blueprint("despachante", __name__, url_prefix="/despachante")

@despachante.route("/escolher", methods=["POST", "GET"])
@login_required
def selecionar_despachante():
    despachantes = User.query.all()
    if request.method == "POST":
        selected_id = request.form.get("despachante_id")
        selected_despachante = User.query.get(selected_id)
        if selected_despachante:
            current_user.despachante = selected_despachante.id
            db.session.commit()
            flash(f"Despachante {selected_despachante.username.capitalize()} selecionado com sucesso!", "success")
            return redirect(url_for("placas.solicitar_placas"))
    return render_template('despachante/despachante.html', despachantes=despachantes)