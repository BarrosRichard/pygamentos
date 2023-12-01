from config.database import db
from config.env import env
from config.response import response
from flask import Blueprint, request, jsonify
import jwt
from models.credit_card_model import CreditCard

class CreditCardBlueprint(Blueprint):
    def __init__(self) -> None:
        super().__init__('credit_card_bp', __name__)

        @self.route('/get_credit_cards', methods=['GET'])
        def get_credit_cards() -> jsonify:
            return self._handle_request(self._get_credit_cards)

        @self.route('/add_credit_card', methods=['POST'])
        def add_credit_card() -> jsonify:
            return self._handle_request(self._add_credit_card)

        @self.route('/remove_credit_card', methods=['DELETE'])
        def remove_credit_card() -> jsonify:
            return self._handle_request(self._remove_credit_card)

    def _handle_request(self, handler_func) -> jsonify:
        try:
            token = request.headers.get('Authorization')
            decoded_token = jwt.decode(jwt=token, key=env('APP_KEY'), options={"verify_signature": False})

            return handler_func(decoded_token)
        except jwt.ExpiredSignatureError:
            return response(status=False, code=401, message='Token expirado.')
        except jwt.InvalidTokenError:
            return response(status=False, code=401, message='Token inválido.')

    def _get_credit_cards(self, decoded_token) -> jsonify:
        credit_cards = db.session.query(CreditCard).filter_by(user_id=decoded_token['user']['id'])

        return response(
            status=True,
            code=200,
            message='A solicitação foi concluída com sucesso.',
            data=[self._format_credit_card(cc) for cc in credit_cards]
        ) if credit_cards else response(status=False, code=404, message='Nenhum cartão de crédito registrado para o usuário atual.')

    def _add_credit_card(self, decoded_token) -> jsonify:
        data = request.json
        new_credit_card = CreditCard(
            user_id=decoded_token['user']['id'],
            number=data['number'],
            validate=data['validate'],
            cvv=data['cvv'],
            description=data.get('description', None)
        )

        db.session.add(new_credit_card)
        db.session.commit()

        return response(status=True, code=200, message='Cartão de crédito adicionado com sucesso.')

    def _remove_credit_card(self, decoded_token) -> jsonify:
        data = request.json
        credit_card = db.session.query(CreditCard).filter_by(id=data['credit_card_id']).first()

        if credit_card and credit_card.user_id == decoded_token['user']['id']:
            db.session.delete(credit_card)
            db.session.commit()
            return response(status=True, code=200, message='Cartão de crédito removido com sucesso.')
        else:
            return response(status=False, code=404, message='Cartão de crédito não encontrado.')

    def _format_credit_card(self, credit_card) -> dict:
        return {
            'id': credit_card.id,
            'number': credit_card.number,
            'validate': credit_card.validate,
            'cvv': credit_card.cvv,
            'description': credit_card.description,
            'created_at': credit_card.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            'updated_at': credit_card.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
