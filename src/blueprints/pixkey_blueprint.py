from config.database import db
from config.env import env
from config.response import response
from flask import Blueprint, request, jsonify
import jwt
from models.user_model import User
from models.pixkey_model import PixKey
from models.pixkey_types_model import PixKeyType

class PixKeyBlueprint(Blueprint):
    def __init__(self) -> None:
        super().__init__('pixkeybp', __name__)

        @self.route('/get_pixkeys', methods=['GET'])
        def get_pixkeys() -> jsonify:
            return self._handle_request(self._get_pixkeys)

        @self.route('/get_pixkey_types', methods=['GET'])
        def get_pixkey_types() -> jsonify:
            return self._handle_request(self._get_pixkey_types)

        @self.route('/add_pixkey_type', methods=['POST'])
        def add_pixkey_type() -> jsonify:
            return self._handle_request(self._add_pixkey_type)

        @self.route('/add_pixkey', methods=['POST', 'PUT'])
        def add_pixkey() -> jsonify:
            return self._handle_request(self._add_pixkey)
        
        @self.route('/search_pixkey', methods=['GET'])
        def search_pixkey() -> jsonify:
            return self._handle_request(self._search_pixkey)

    def _handle_request(self, handler_func) -> jsonify:
        try:
            token = request.headers.get('Authorization')
            decoded_token = jwt.decode(jwt=token, key=env('APP_KEY'), options={"verify_signature": False})

            return handler_func(decoded_token)
        except jwt.ExpiredSignatureError:
            return response(status=False, code=401, message='Token expirado.')
        except jwt.InvalidTokenError:
            return response(status=False, code=401, message='Token inválido.')

    def _get_pixkeys(self, decoded_token) -> jsonify:
        pixkeys = db.session.query(PixKey).filter_by(user_id=decoded_token['user']['id']).all()

        return response(
            status=True,
            code=200,
            message='A solicitação foi concluída com sucesso.',
            data=[self._format_pixkey(pk) for pk in pixkeys]
        ) if pixkeys else response(status=False, code=404, message='Nenhuma chave pix registrada para o usuário atual.')

    def _get_pixkey_types(self, decoded_token) -> jsonify:
        pixkey_types = db.session.query(PixKeyType).all()

        return response(
            status=True,
            code=200,
            message='A solicitação foi concluída com sucesso.',
            data=[{'id': pkt.id, 'description': pkt.description} for pkt in pixkey_types]
        )

    def _add_pixkey_type(self, decoded_token) -> jsonify:
        data = request.json
        new_pixkey_type = PixKeyType(description=data['description'])

        db.session.add(new_pixkey_type)
        db.session.commit()

        return response(status=True, code=200, message='Tipo de chave pix adicionado com sucesso.')

    def _add_pixkey(self, decoded_token) -> jsonify:
        data = request.json
        check_pixkey = db.session.query(PixKey).filter_by(key=data['key']).first()

        if check_pixkey:
            return response(status=False, code=404, message='Essa chave pix já foi utilizada.')
        else:
            new_pixkey = PixKey(user_id=decoded_token['user']['id'], key_type_id=data['key_type_id'], key=data['key'])
            db.session.add(new_pixkey)
            db.session.commit()

            return response(status=200, code=200, message='Chave pix adicionada com sucesso.')

    def _search_pixkey(self, decoded_token) -> jsonify:
        data = request.json

        pixkey = db.session.query(PixKey).filter_by(key=data['pixkey']).first()

        if pixkey:
            user = db.session.query(User).filter_by(id=pixkey.user_id).first()

            if user:
                return response(status=True, code=200, message='A solicitação foi concluída com sucesso.', data={'id': user.id, 'username': user.username})
            else:
                return response(status=False, code=404, message='Nenhuma chave pix foi encontrada.')
        else:
            return response(status=False, code=404, message='Nenhuma chave pix foi encontrada.')

    def _format_pixkey(self, pixkey) -> dict:
        return {
            'id': pixkey.id,
            'type': db.session.query(PixKeyType).filter_by(id=pixkey.key_type_id).first().description,
            'key': pixkey.key
        }