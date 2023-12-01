from config.database import db
from config.env import env
from config.response import response
from flask import Blueprint, request, jsonify
import jwt
from models.user_model import User
from models.transaction_model import Transaction
from models.transaction_types_model import TransactionTypes
from datetime import datetime

class TransactionBlueprint(Blueprint):
    def __init__(self) -> None:
        super().__init__('transactionbp', __name__)

        @self.route('/get_balance', methods=['GET'])
        def get_balance() -> None:
            return self._handle_request(self._get_balance)

        @self.route('/deposit', methods=['POST'])
        def deposit() -> None:
            return self._handle_request(self._deposit)

        @self.route('/get_transactions', methods=['GET'])
        def get_transactions() -> jsonify:
            return self._handle_request(self._get_transactions)
        
        @self.route('/get_transaction_types', methods=['GET'])
        def get_transaction_types() -> jsonify:
            return self._handle_request(self._get_transaction_types)
        
        @self.route('/get_transaction_tax', methods=['GET'])
        def get_transaction_tax() -> jsonify:
            return self._handle_request(self._get_transaction_tax)

        @self.route('/add_transaction_type', methods=['POST'])
        def add_transaction_type() -> None:
            return self._handle_request(self._add_transaction_type)

        @self.route('/send_transaction', methods=['POST'])
        def send_transaction() -> jsonify:
            return self._handle_request(self._send_transaction)
        
        @self.route('/get_full_transaction', methods=['GET'])
        def get_full_transaction() -> jsonify:
            return self._handle_request(self._get_full_transaction)

    def _handle_request(self, handler_func) -> jsonify:
        try:
            token = request.headers.get('Authorization')
            decoded_token = jwt.decode(jwt=token, key=env('APP_KEY'), options={"verify_signature": False})
            return handler_func(decoded_token)
        except jwt.ExpiredSignatureError:
            return response(status=False, code=401, message='Token expirado.')
        except jwt.InvalidTokenError:
            return response(status=False, code=401, message='Token inválido.')

    def _get_balance(self, decoded_token) -> jsonify:
        user = db.session.query(User).filter_by(id=decoded_token['user']['id']).first()
        payments = db.session.query(Transaction).filter_by(user_id=decoded_token['user']['id'])
        received = db.session.query(Transaction).filter_by(user_dest=decoded_token['user']['id'])

        return response(
            status=True,
            code=200,
            message='A solicitação foi concluída com sucesso.',
            data={
                'balance': user.balance,
                'payments': [self._format_transaction(p, is_payment=True) for p in payments],
                'received': [self._format_transaction(r) for r in received]
            }
        )

    def _deposit(self, decoded_token) -> None:
        data = request.json
        user_dest = db.session.query(User).filter_by(id=decoded_token['user']['id']).first()
        amount = data['amount']

        new_transaction = Transaction(
            user_id=0,
            user_dest=decoded_token['user']['id'],
            transaction_type_id=1,
            amount=amount,
            description='DEPOSITO'
        )

        user_dest.balance += amount

        db.session.add(new_transaction)
        db.session.add(user_dest)
        db.session.commit()

        return response(status=True, code=200, message='Depósito realizado com sucesso.')

    def _get_transactions(self, decoded_token) -> jsonify:
        payments = db.session.query(Transaction).filter_by(user_id=decoded_token['user']['id'])
        received = db.session.query(Transaction).filter_by(user_dest=decoded_token['user']['id'])

        return response(
            status=True,
            code=200,
            message='A solicitação foi concluída com sucesso.',
            data={
                'payments': [self._format_transaction(p, is_payment=True) for p in payments],
                'received': [self._format_transaction(r) for r in received]
            }
        )

    def _get_transaction_types(self, decoded_token) -> jsonify:
        transaction_types = db.session.query(TransactionTypes).all()
        transaction_types_list = [{'id': tt.id, 'description': tt.description, 'tax': tt.tax} for tt in transaction_types]
        return response(status=True, code=200, message='Tipos de transações obtidos com sucesso', data=transaction_types_list)

    def _add_transaction_type(self, decoded_token) -> None:
        data = request.json

        new_trans_type = TransactionTypes(
            description=data['description'],
            tax=data['tax']
        )

        db.session.add(new_trans_type)
        db.session.commit()

        return response(status=True, code=200, message='Tipo de transação adicionado com sucesso.')

    def _send_transaction(self, decoded_token) -> jsonify:
        data = request.json
        user_id = decoded_token['user']['id']
        user = db.session.query(User).filter_by(id=user_id).first()
        receiver = db.session.query(User).filter_by(id=data['receiver']).first()

        if not receiver:
            return response(status=False, code=404, message='Chave PIX do destinatário não encontrada.')

        transaction_type = db.session.query(TransactionTypes).filter_by(id=data['transaction_type']).first()

        if not transaction_type:
            return response(status=False, code=404, message='Tipo de transação não encontrado.')

        total_amount = data['amount'] * (1 + transaction_type.tax)

        if user.balance < total_amount:
            return response(status=False, code=400, message='Saldo insuficiente.')

        new_transaction = Transaction(
            user_id=user_id,
            user_dest=receiver.id,
            transaction_type_id=data['transaction_type'],
            amount=total_amount,
            description='TRANSFERENCIA'
        )

        user.balance -= total_amount
        receiver.balance += data['amount'] 

        db.session.add(new_transaction)
        db.session.commit()

        return response(status=True, code=200, message='Transação realizada com sucesso.')

    def _get_transaction_tax(self, decoded_token) -> jsonify:
        data = request.json
        transaction_type_id = data['transaction_type_id']
        transaction_type = db.session.query(TransactionTypes).filter_by(id=transaction_type_id).first()

        if not transaction_type:
            return response(status=False, code=404, message='Tipo de transação não encontrado.')

        return response(
            status=True,
            code=200,
            message='Taxa de transação obtida com sucesso.',
            data={'tax': transaction_type.tax}
        )

    def _get_full_transaction(self, decoded_token) -> jsonify:
        send = db.session.query(Transaction).filter_by(user_id=decoded_token['user']['id'])
        receive = db.session.query(Transaction).filter_by(user_dest=decoded_token['user']['id'])

        transactions = send.union(receive).all()

        if not transactions:
            return response(status=False, code=404, message='Transação não encontrada.')

        formatted_transaction = [{
            'id': t.id,
            'type': db.session.query(TransactionTypes).filter_by(id=t.transaction_type_id).first().description,
            'description': t.description,
            'amount': t.amount,
            'datetime': datetime.strftime(t.created_at, "%Y-%m-%d %H:%M:%S"),
            'receiver': db.session.query(User).filter_by(id=t.user_dest).first().username,
            'sender': db.session.query(User).filter_by(id=t.user_id).first().username
        } for t in transactions]

        return response(
            status=True,
            code=200,
            message='Detalhes da transação obtidos com sucesso.',
            data=formatted_transaction
        )

    def _format_transaction(self, transaction, is_payment=False) -> dict:
        amount = transaction.amount * -1 if is_payment else transaction.amount
        return {
            'id': transaction.id,
            'type': db.session.query(TransactionTypes).filter_by(id=transaction.transaction_type_id).first().description,
            'description': transaction.description,
            'amount': amount,
            'paid_for_received_from': db.session.query(User).filter(User.id==transaction.user_dest if is_payment else User.id==transaction.user_id).first().username,
            'datetime': datetime.strftime(transaction.created_at, "%Y-%m-%d %H:%M:%S")
        }
