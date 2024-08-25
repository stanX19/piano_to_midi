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
                try:
                    self.cache[instance] = self.func(instance)
                except BaseException as exc:
                    del self.cache[instance]
                    raise exc
            while self.cache[instance] is Pending:
                print("blocking")
                pass
            return self.cache[instance]

        def fset(instance, value):
            self.cache[instance] = value

        super().__init__(fget, fset)
