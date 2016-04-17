# Simple Interceptor

It is a simple tool that can be used to intercept methods of classes to apply advices on them.

## Installation

The package is registered with PyPi and can be found [here](https://pypi.python.org/pypi/SimpleInterceptor/0.1.dev1). 
Though ```pip search SimpleInterceptor``` doesn't return anything, installation has been tested using 
[TestPyPi](https://testpypi.python.org/pypi). Alternatively, the package can be cloned or downloaded, extracted and 
following can be run

- *Install* using ```python setup.py install```
- *Run Tests* using ```python setup.py test```

## Example

If we were to implement a bank transaction logic, it could be as simple as this.

    class BankTransaction(object):
        def transfer(self, amt):
            print "Transferring Rs. %d" % amt

And transaction would be done this simply as well.

    obj = BankTransaction()
    obj.transfer(1000)
    
![Non-intercept Example](example/non-intercept.jpg?raw=true "Non-intercept Example")

Now, there could be various other concerns related to this requirement - *logging, checking if balance is 
available, notifying user about the transaction status* etc. We could had written all of this logic there. 
But in order to modularise it better or separate the cross-cutting concerns, we follow principles of AOP 
and apply the other concerns(advices) by intercepting the core method. This simple library is intended to 
do this.

Say the above concerns are implemented this trivially.

    def start_transaction_log(*args, **kwargs):
        print "Starting transaction"

    def check_balance_available(*args, **kwargs):
        print "Balance check logic says Transaction allowed"

    def send_notification(*args, **kwargs):
        print "Transaction successful"

Now, in order to apply these logics to the ```transfer``` method, we would need to create an aspect and 
decorate the ```BankTransaction``` class with the ```intercept``` decorator, featured by the tool, as shown 
under. Instead of using transfer we could had used any regex pattern to match the method name. This allows 
to intercept multiple methods using the same pattern.

    aspects = dict()
    aspects[r'transfer'] = dict(
        before=start_transaction_log,
        around_before=check_balance_available,
        after_success=send_notification)

    from interceptor import intercept

    BankTransaction = intercept(aspects)(BankTransaction)

    obj = BankTransaction()
    obj.transfer(1000)

![Intercept Example](example/intercept.jpg?raw=true "Intercept Example")

## Advices honoured

The tool accepts following self-explanatory advices. *before* logic is run before *around_before* and 
*around_after* is run before *after_success*. *after_exc* can be used to write exception logic. *around_after* 
doesn't run in case of exception. 

- before
- around_before
- after_exc
- around_after
- after_success
- after_finally