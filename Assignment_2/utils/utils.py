from ReturnValueThread import ReturnValueThread
from threading import Thread

def run_thread(fn, args):
    my_thread = Thread(target=fn, args=args)
    my_thread.daemon = True
    my_thread.start()
    return my_thread


def run_thread_returnable(fn, args):
    thread1 = ReturnValueThread(target=fn, args=args)
    # my_thread = Thread(target=fn, args=args)
    # my_thread.daemon = True
    thread1.start()
    result = thread1.join()
    print(f'returns ({args}) = {result}')
    return result
