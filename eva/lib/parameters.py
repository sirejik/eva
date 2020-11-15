class Parameters:
    def __init__(self, params=None):
        self._params = params or {}
        self._backup = {}

    def __getattribute__(self, key):
        if key == '_params':
            return object.__getattribute__(self, key)

        return self._params[key]

    def __setattr__(self, key, value):
        if key == '_params':
            return object.__setattr__(self, key, value)

        self._params[key] = value

    def update(self, params):
        for key, value in params:
            self._params[key] = value

    def backup(self):
        self._backup = self._params

    def restore(self):
        self._params = self._backup
