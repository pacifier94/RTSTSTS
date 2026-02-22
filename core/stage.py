import threading
import queue
import time

class Stage(threading.Thread):
    def __init__(self, name, input_q=None, output_q=None):
        super().__init__(daemon=True)
        self.name = name
        self.input_q = input_q
        self.output_q = output_q
        self.running = True

    def process(self, data):
        raise NotImplementedError

    def run(self):
        while self.running:
            try:
                if self.input_q:
                    data = self.input_q.get(timeout=0.1)
                else:
                    data = None

                result = self.process(data)

                if self.output_q and result is not None:
                    self.output_q.put(result)

            except queue.Empty:
                continue

    def stop(self):
        self.running = False
