class Service:
    def __init__(self, name, uniform_type_id):
        self.name = name
        self.uniform_type_id = uniform_type_id


class Characteristic:
    def __init__(self, name, uniform_type_id):
        self.name = name
        self.uniform_type_id = uniform_type_id


class Descriptor:
    def __init__(self, name, uniform_type_id):
        self.name = name
        self.uniform_type_id = uniform_type_id


class Member:
    def __init__(self, name):
        self.name = name


class ServiceClass:
    def __init__(self, name, specification):
        self.name = name
        self.specification = specification


class ServiceProtocol:
    def __init__(self, name, specification):
        self.name = name
        self.specification = specification
