"""Sample advices for bank transaction"""

# pylint: disable=C0111,W0613


class BankAdvices(object):
    """Bank transaction secondary concerns"""
    @staticmethod
    def start_transaction_log(*args, **kwargs):
        print "Starting transaction"

    @staticmethod
    def check_balance_available(*args, **kwargs):
        print "Balance check logic says Transaction allowed"

    @staticmethod
    def send_notification(*args, **kwargs):
        print "Transaction successful"


class CookingAdvices(object):
    """Cooking secondary concerns"""
    @staticmethod
    def buy_grocery(*args, **kwargs):
        print "Bought grocery"

    @staticmethod
    def ingredients_not_ready(*args, **kwargs):
        print "Ingredients not ready"

    @staticmethod
    def prepare_for_cooking(*args, **kwargs):
        print "Prepare Ingredients for cooking"

    @staticmethod
    def notify_cooked(*args, **kwargs):
        print "Food cooked"
