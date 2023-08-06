from solar_crypto.constants import TRANSACTION_HTLC_LOCK, TRANSACTION_TYPE_GROUP
from solar_crypto.identity import address
from solar_crypto.transactions.builder.base import BaseTransactionBuilder


class HtlcLock(BaseTransactionBuilder):

    transaction_type = TRANSACTION_HTLC_LOCK

    def __init__(
        self,
        recipient_id,
        amount,
        secret_hash,
        expiration_type,
        expiration_value,
        memo=None,
        fee=None,
    ):
        """Create a timelock transaction

        Args:
            recipient_id (str): recipient identifier
            amount (int): amount of coins you want to transfer
            secret_hash (str): a hash of the secret. The SAME hash must be used in the corresponding “claim” transaction
            expiration_type (int): type of the expiration. Either block height or network epoch timestamp based
            expiration_value (int): Expiration of transaction in seconds or height depending on expiration_type
            memo (str): value for the optional text field
            fee (int, optional): fee used for the transaction (default is already set)
        """
        super().__init__()

        if not address.validate_address(recipient_id):
            raise ValueError("Invalid recipient address")

        self.transaction.recipientId = recipient_id

        if type(amount) == int and amount > 0:
            self.transaction.amount = amount
        else:
            raise ValueError("Amount is not valid")

        self.transaction.typeGroup = self.get_type_group()

        self.transaction.asset["lock"] = {
            "secretHash": secret_hash,
            "expiration": {"type": expiration_type, "value": expiration_value},
        }

        self.transaction.memo = memo.encode() if memo else None

        if fee:
            self.transaction.fee = fee

    def get_type_group(self):
        return TRANSACTION_TYPE_GROUP.CORE.value
