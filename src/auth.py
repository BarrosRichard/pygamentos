from config.database import db
from config.env import env
from config.response import response
from models.user_model import User
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import jwt

class Auth(Blueprint):
    def __init__(self) -> None:
        super().__init__('authbp', __name__)

        @self.route('/register', methods=['POST'])
        def register() -> jsonify:
            data = request.json

            check_user = db.session.query(User).filter_by(username=data['username']).first()

            if check_user:
                return response(
                    status=False,
                    code=404,
                    message='O usuário informado já está registrado.',
                )
            else:
                new_user = User(
                    username=data['username'],
                    password=generate_password_hash(data['password'], 'pbkdf2:sha256')
                )
                db.session.add(new_user)
                db.session.commit()

                return response(
                    status=True,
                    code=200,
                    message='Usuário registrado com sucesso.',
                )
            
        @self.route('/login', methods=['POST'])
        def login() -> jsonify:
            data = request.json

            user = db.session.query(User).filter_by(username=data['username']).first()

            if user:
                if check_password_hash(user.password, data['password']):
                    token = jwt.encode({
                        'user': {
                            'id': user.id,
                            'username': user.username,
                            'balance': user.balance,
                        },
                        'exp': datetime.utcnow() + timedelta(minutes=30)
                    }, env('APP_KEY'))

                    return response(
                        status=True,
                        code=200,
                        message='Usuário autenticado com sucesso.',
                        data={'token': token}
                    )
                else:
                    return response(
                        status=False,
                        code=401,
                        message='Credenciais inválidas.'
                    )
            else:
                return response(
                        status=False,
                        code=401,
                        message='Credenciais inválidas.'
                    )
