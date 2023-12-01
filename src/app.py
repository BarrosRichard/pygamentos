from config.env import env
from config.database import db
from flask import Flask
from flask_migrate import Migrate
from auth import Auth

from blueprints.transactions_blueprint import TransactionBlueprint
from blueprints.pixkey_blueprint import PixKeyBlueprint
from blueprints.credit_card_blueprint import CreditCardBlueprint

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = env("SQLALCHEMY_DATABASE_URI")
db.init_app(app)
migrate = Migrate(app, db)
auth = Auth()

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(TransactionBlueprint(), url_prefix='/transaction')
app.register_blueprint(PixKeyBlueprint(), url_prefix='/pixkey')
app.register_blueprint(CreditCardBlueprint(), url_prefix='/credit_card')

if __name__ == '__main__':
    app.run(debug=True)