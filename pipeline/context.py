class Context:
    def __init__(self):
        self.next = None
        self.engine = None
        self.queries = None

    def call(self, callee):
        if callee is None:
            return
        else:
            callee.run(self)
            self.call(callee.next)

    def setEngine(self, engine):
        self.engine = engine

    def setQueries(self, queries):
        self.queries = queries