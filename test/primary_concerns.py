"""Sample bank transaction implementation"""

# pylint: disable=C0111,R0201


class BankTransaction(object):
    """Bank transaction implementations"""
    def transfer(self, amt):
        print "Transferring Rs. %d" % amt

    def credit(self, amt):
        print "Adding Rs. %d to account balance" % amt

    @staticmethod
    def update_passbook():
        print "Updated passbook"


class FoodPreparation(object):
    """Cooking food implementations"""
    dish_count = 3

    def prepare_curry(self):
        raise Exception

    @classmethod
    def get_dish_count(cls):
        print "There are %d items" % cls.dish_count

    def prepare_chapati(self, count):
        print "%d chapatis ready" % count
