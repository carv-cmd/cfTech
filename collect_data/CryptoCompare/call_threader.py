# Credit to "Andrea" for the threading implementation.
# Wasn't in the mood to reinvent the wheel mid project and this works very well.
# Kudos to Andrea from stackExchange
# https://stackoverflow.com/questions/5179467/equivalent-of-setinterval-in-python
import threading
import time


def set_interval(interval, times=-1):
    """ This is the actual decorator w/ fixed interval and times parameters """
    def outer_wrap(function):
        """ This will be the function called """
        def wrap(*args, **kwargs):
            stop = threading.Event()

            def inner_wrap():
                """ Function to be executed in a different thread to simulate setInterval """
                i = 0
                while i != times and not stop.isSet():
                    stop.wait(interval)
                    function(*args, **kwargs)
                    i += 1

            t = threading.Timer(0, inner_wrap)
            t.daemon = True
            t.start()
            return stop
        return wrap
    return outer_wrap


if __name__ == "__main__":
    # Set the wait time for repeat
    @set_interval(1)
    def foo(a):
        print(a)

    stopping = foo('bar')

    time.sleep(360)
    stopping.set()

else:
    print(f'\nCalled Helper Module: "{__name__}"')
