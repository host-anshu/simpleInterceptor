"""Business logic to print output"""

# pylint: disable=C0103,R0201,W0401


class PrintOutput(object):
    """Class to print outputs"""
    def hello_world(self):
        """Prints Hello world!"""
        print "Hello world!"

    def division(self, x, y):
        """Prints division of two numbers"""
        print x / y


if __name__ == '__main__':
    # =========================================================================
    print "Non-intercepted execution"
    print "#" * 30
    obj = PrintOutput()
    obj.hello_world()                 # prints ""Hello world!""
    obj.division(4, 2)                # prints 2
    # obj.division(4, 0)              # Throws error
    print "\n"

    # =========================================================================
    from example.print_output.advice import *
    from interceptor import intercept

    def generate_sample_aspects():
        """Returns aspects for the PrintOutput class"""
        aspects = dict()
        aspects[r'.*'] = dict(
            # advices for the joint-point(method name) matching any character
            before=before,
            after_finally=after_finally,
        )
        aspects[r'hello_world'] = dict(
            # advices for the joint-point(method name) matching hello_world
            around_before=around_before,
            around_after=around_after,
            after_success=after_returning,
        )
        aspects[r'division'] = dict(
            # advices for the joint-point(method name) matching division
            around_before=around_before,
            after_exc=after_throwing,
            around_after=around_after,
            after_success=after_returning,
        )
        return aspects

    sample_aspects = generate_sample_aspects()
    PrintOutput = intercept(sample_aspects)(PrintOutput)  # intercept the client class

    print "Intercepted execution"
    print "#" * 30
    obj = PrintOutput()
    # prints before, around_before, around_after, after_returning, after_finally advices
    # wrapped around "Hello World!"
    obj.hello_world()
    print "\n"
    # prints before, around_before, around_after, after_returning, after_finally advices
    # wrapped around 2
    obj.division(4, 2)
    print "\n"
    # prints before, around_before, around_after, after_throwing, after_finally advices
    obj.division(4, 0)
