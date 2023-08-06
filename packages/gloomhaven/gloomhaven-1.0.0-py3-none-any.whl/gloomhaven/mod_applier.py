class ModDeckApplier(dict):
    def __init__(self, default_fn):
        self.default_fn = default_fn

    def __missing__(self, key):
        return self.default_fn(key)
