from grupo_andrade.main import create_app

app = create_app()

if __name__ == '__main__':

    # app/__init__.py ou onde você cria sua aplicação
    
    app.run(debug=False)