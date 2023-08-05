from vayaAuto.option import Option


class Section(object):
    EXPORT_PREFIX = 'saveFile_'
    VIS_PREFIX = 'visShow'
    SENSOR_ENABLE_PREFIX = 'SensorEnable'
    # VAYA_CONFIG = get_vaya_config()

    def __init__(self, name):
        self._name = name
        self.options = {}

    def add_option(self, name):
        # value_type = type(self.VAYA_CONFIG[self._name][name])
        option = Option(name)
        self.options.update({name: option})

    def keys(self):
        return self.options.keys()

    def items(self):
        return self.options.items()

    def __iter__(self):

        for (name, option) in self.options.items():
            yield name, option

    def __hash__(self):
        return hash(tuple(sorted(self.options)))

    def __setitem__(self, key, value):
        self.options[key] = value

    def __getitem__(self, key):
        return self.options[key]

    def __str__(self):
        return f"{self._name}"

    def __repr__(self):
        return self._name