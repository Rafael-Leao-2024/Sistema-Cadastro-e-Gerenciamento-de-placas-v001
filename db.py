from grupo_andrade.main import db, create_app

app = create_app()

with app.app_context():
    db.create_all()
    print("Tabelas criadas com sucesso!")

