from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from grupo_andrade.main import db
from grupo_andrade.models import User

admin = Blueprint('admin', __name__)

@admin.route('/admin', methods=["GET", "POST"])
@login_required
def admin_permissao():
    usuarios = User.query.all()
    return render_template('admin/admin.html', usuarios=usuarios)


@admin.route('/admin/<int:id_usuario>', methods=["GET", "POST"])
@login_required
def permitir(id_usuario):
    usuario = User.query.filter(User.id==id_usuario).first()
    if not usuario:
        flash(message="Usuario nao encontrado", category='warning')
        return redirect(url_for("admin.admin_permissao"))
    if usuario.is_admin:
        usuario.is_admin = False
        flash(message=f"Usuario {usuario.username.upper()} desabilitado em permissao de admin", category='danger')
    else:
        usuario.is_admin = True
        flash(message=f"Usuario {usuario.username.upper()} agora tem permissao de admin", category='success')
    db.session.commit()
    return redirect(url_for("admin.admin_permissao"))