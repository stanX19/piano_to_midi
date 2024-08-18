import weakref

class Pending:
    pass

class SettableCachedProperty(property):
    def __init__(self, func):
        self.func = func
        self.cache = weakref.WeakKeyDictionary()

        def fget(instance):
            if instance not in self.cache:
                self.cache[instance] = Pending
                self.cache[instance] = self.func(instance)
            while self.cache[instance] is Pending:
                pass
            return self.cache[instance]

        def fset(instance, value):
            self.cache[instance] = value

        super().__init__(fget, fset)
