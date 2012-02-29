import fudge

class ShuntMixin(object):
    def __patch_method__(self, method_name, expects_call=True):
        fake_method = fudge.Fake()
        if expects_call:
            fake_method.expects_call()
        else:
            fake_method.is_callable()
        setattr(self, method_name, fake_method)
        return fake_method

def shunt_class(Klass):
    """Creates a shunt for any object"""
    class ShuntClass(Klass, ShuntMixin):
        pass
    return ShuntClass
