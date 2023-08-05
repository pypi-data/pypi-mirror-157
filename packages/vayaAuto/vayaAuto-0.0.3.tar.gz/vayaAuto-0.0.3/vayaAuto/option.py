class Option(object):

    def __init__(self, name, value_type=None):
        self._name = name
        self._type = value_type
        self._value = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        # if isinstance(value, self._type):
        self._value = value
        # else:
        #     print(f'Option {self._name} - \ninvalid value type {type(value)}, expect {self._type}')

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def isOn(self):
        if self._value == 'true':
            return True
        else:
            return False

    def isOff(self):
        return not self.isOn()

    def __str__(self):
        return self._name