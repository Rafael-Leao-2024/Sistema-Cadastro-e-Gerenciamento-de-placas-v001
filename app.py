from grupo_andrade.main import create_app


if __name__ == '__main__':
    app = create_app()

    # app/__init__.py ou onde você cria sua aplicação
    
    app.run(host='0.0.0.0', port=5000, debug=True)