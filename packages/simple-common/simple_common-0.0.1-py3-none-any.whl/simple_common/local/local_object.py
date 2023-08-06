__all__ = ['local']

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    try:
        from thread import get_ident
    except ImportError:
        from _thread import get_ident


class LocalObject(object):
    def __init__(self):

        object.__setattr__(self, '__xstorage__', {})
        object.__setattr__(self, '__xident_func__', get_ident)

    def __getattr__(self, name):
        try:
            return self.__xstorage__[self.__xident_func__()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = self.__xident_func__()
        xstorage = self.__xstorage__
        try:
            xstorage[ident][name] = value
        except KeyError:
            xstorage[ident] = {name: value}

    def __delattr__(self, name):
        try:
            del self.__xstorage__[self.__xident_func__()][name]
        except KeyError:
            raise AttributeError(name)


local = LocalObject()
