class Arguments:
    def __init__(self, path='', **kwargs):
        self.path = path
        self.output = kwargs.get('output', '/tmp/deguard')
        self.timeout = kwargs.get('timeout', 600)
        try:
            self.timeout = int(self.timeout)
        except ValueError:
            print('Timeout is not a number revert to default')
            self.timeout = 600
