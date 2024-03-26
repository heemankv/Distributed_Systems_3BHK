from threading import Thread

def run_thread(fn, args):
    my_thread = Thread(target=fn, args=args)
    my_thread.daemon = True
    my_thread.start()
    return my_thread