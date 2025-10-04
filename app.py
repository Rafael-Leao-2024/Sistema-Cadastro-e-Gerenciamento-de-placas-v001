from grupo_andrade.main import create_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate



app = create_app()

db = SQLAlchemy()
migrate = Migrate(app, db=db)


if __name__ == '__main__':    
    app.run(debug=False)