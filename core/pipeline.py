class Pipeline:
    def __init__(self, stages):
        self.stages = stages

    def start(self):
        for s in self.stages:
            s.start()

    def stop(self):
        for s in self.stages:
            s.stop()
