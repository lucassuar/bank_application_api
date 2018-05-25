import os

from flask import g, request
from flask_restful import Resource

try:
    from api.models import User, Transaction
    from api.helper.authorization import token_required
    from api.helper.helper import (
        validate_request_keys, validate_request_type, 
        validate_request_json, bapp_errors, 
    )
except ImportError:
    from bank_application_api.api.models import User, Transaction
    from bank_application_api.api.helper.authorization import token_required
    from bank_application_api.api.helper.helper import (
        validate_request_keys, validate_request_type, 
        validate_request_json, bapp_errors
    )


class DepositResource(Resource):

    @token_required
    def post(self):
        json_input = request.get_json()

        fields = '(amount, account_number)'
        if not validate_request_keys(json_input, ['account_number', 'amount']):
            return bapp_errors(
                'These fields are required on make deposit {0}'.format(fields), 
                400
            )

        # handling amount exceptions
        try:
            _amount = float(json_input['amount'])
        except:
            return bapp_errors("Your account amount must be a number", 400)
        if _amount < 100:
                return bapp_errors(
                    "Sorry, you cannot deposit less than \u20A6 100.00",
                    400
                )
        _account_number = str(json_input["account_number"])

        json_input.pop('amount', None)
        if not validate_request_type(str, json_input):
            return bapp_errors(
                'Account number cannot be empty', 
                400
            )

        # to prevent tokens with string ids from breaking the app
        try:
            _user_id = int(g.current_user.id)
        except:
            return bapp_errors("User does not exist", 404)

        _user = User.query.get(int(g.current_user.id))
        if not _user:
            return bapp_errors("User does not exist", 404)

        _receiver = User.query.filter(User.account_number==_account_number).first()
        if not _receiver:
            return bapp_errors(
                "This account number does not exist ({0})".format(_account_number),
                400
            )

        # updating reciever's account 
        _receiver.account_amount += _amount
        _receiver.save()

        # saving transaction
        new_transaction = Transaction(
            user_id=_receiver.id,
            transaction_type="credit",
            transaction_amount=_amount
        ) 
        new_transaction.save()

        return {
            'status': 'success',
            'data': {
                'transaction': new_transaction.serialize(),
                'message': 'Transaction succesfully completed',
            }
        }, 201