class Metrics:
    def __init__(self):
        self.metrics = []

    def set_metrics(self, summary):
        self.metrics.append(summary)

    def get_metrics(self):
        return self.metrics
