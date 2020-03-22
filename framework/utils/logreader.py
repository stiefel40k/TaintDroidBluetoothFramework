import threading
import queue


class AsynchronousFileReader(threading.Thread):
    """
    Helper class to implement asynchronous reading of a file
    in a separate thread. Pushes read lines on a queue to
    be consumed in another thread.
    """

    def __init__(self, process, q):
        assert isinstance(q, queue.Queue)
        assert callable(process.stdout.readline)
        threading.Thread.__init__(self)
        self._process = process
        self._fd = process.stdout
        self._queue = q
        self.cont = True

    def run(self):
        """The body of the tread: read lines and put them on the queue."""
        for line in iter(self._fd.readline, ''):
            if not self.cont and self._queue.empty():
                break
            if len(line) > 0:
                self._queue.put(line)

    def eof(self):
        """Check whether there is no more content to expect."""
        return not self.is_alive() or (self._queue.empty() and self._process.poll() is not None)
