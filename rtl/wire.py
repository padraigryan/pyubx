class Wire:
    def __init__(self, name, size=1, comment=""):
        self.name = name
        self.size = size
        self.comment = comment
        self.module_conn = []           # List of tuples; (module, port)

    def connect(self, module, port):
        self.module_conn.append( (module,port) )