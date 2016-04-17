"""Test suite for interceptor"""

import sys
import unittest

from StringIO import StringIO

from interceptor import intercept
from test.advices import BankAdvices, CookingAdvices
from test.primary_concerns import BankTransaction, FoodPreparation

NonInterceptedBankTransaction = type(  # Clone BankTransaction before it is intercepted
    "NonInterceptedBankTransaction", BankTransaction.__bases__, dict(BankTransaction.__dict__))


class CapturePrints(unittest.TestCase):
    """Capture print by reassigning sys.stdout for the duration of the test"""
    def setUp(self):
        self.saved_stdout = sys.stdout
        sys.stdout = StringIO()

    def tearDown(self):
        sys.stdout = self.saved_stdout


class NonInterceptedTest(CapturePrints):
    """Non-intercepted primary concern test suite"""
    def test_transfer(self):
        """Should generate non-intercepted output"""
        obj = NonInterceptedBankTransaction()
        obj.transfer(1000)
        self.assertEquals(sys.stdout.getvalue().strip(), "Transferring Rs. 1000")


class InterceptedTest(CapturePrints):
    """Intercepted primary concern test suite"""
    @classmethod
    def setUpClass(cls):
        # Bank setup
        banking_aspects = {
            r'transfer': dict(before=BankAdvices.check_balance_available),
            r'.*': dict(
                before=BankAdvices.start_transaction_log,
                after_success=BankAdvices.send_notification)
        }
        intercept(banking_aspects)(BankTransaction)
        cls.bank_obj = BankTransaction()
        # Cooking setup
        cooking_aspects = {
            r'prepare_curry': dict(
                before=(CookingAdvices.buy_grocery, CookingAdvices.prepare_for_cooking),
                after_exc=CookingAdvices.ingredients_not_ready,
                after_success=CookingAdvices.notify_cooked),
            r'get_dish_count': dict(around_before=CookingAdvices.notify_cooked)
        }
        intercept(cooking_aspects)(FoodPreparation)
        cls.cook_obj = FoodPreparation()

    def test_wildcard(self):
        """Wildcard should match non-mentioned method"""
        expected_out = '\n'.join([
            "Starting transaction",
            "Adding Rs. 1000 to account balance",
            "Transaction successful"
        ])
        self.bank_obj.credit(1000)
        self.assertEquals(sys.stdout.getvalue().strip(), expected_out)

    def test_method_priority(self):
        """Conflicting advice should resolve to joint-point same as method name over wildcard"""
        expected_out = '\n'.join([
            "Balance check logic says Transaction allowed",
            "Transferring Rs. 1000",
            "Transaction successful"
        ])
        self.bank_obj.transfer(1000)
        self.assertEquals(sys.stdout.getvalue().strip(), expected_out)

    def test_staticmethod(self):
        """Staticmethod don't work now"""
        self.bank_obj.update_passbook()
        self.assertEquals(sys.stdout.getvalue().strip(), "Updated passbook")

    def test_multiple_advices(self):
        """All implementations for the same advice should apply"""
        expected_out = '\n'.join([
            "Bought grocery",
            "Prepare Ingredients for cooking",
            "Ingredients not ready"
        ])
        self.cook_obj.prepare_curry()
        self.assertEquals(sys.stdout.getvalue().strip(), expected_out)

    def test_classmethod(self):
        """Classmethod should work"""
        expected_out = '\n'.join([
            "Food cooked",
            "There are 3 items"
        ])
        self.cook_obj.get_dish_count()
        self.assertEquals(sys.stdout.getvalue().strip(), expected_out)

    def test_no_matching_method(self):
        """Method not advised should behave normally"""
        self.cook_obj.prepare_chapati(4)
        self.assertEquals(sys.stdout.getvalue().strip(), "4 chapatis ready")


if __name__ == '__main__':
    unittest.main()
