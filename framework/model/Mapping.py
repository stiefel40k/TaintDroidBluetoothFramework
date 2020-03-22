class Variable:
    """
    Represents the mapping of a class variable from the original name of the
    variable to the new name
    """
    def __init__(self, original_name, new_name, var_type):
        """
        Class initializer
        :param original_name: The original name of the class before mapping
        :type original_name: str
        :param new_name: The new name of the class after mapping
        :type new_name: str
        :param var_type: The type of the variable
        :type var_type: str
        """
        self.original_name = original_name
        self.new_name = new_name
        self.var_type = var_type


class Method:
    """
    Represents the mapping of a method from the original name of the method
    to the new name
    """
    def __init__(self, original_name, new_name, ret_val, parameters):
        """
        Class initializer
        :param original_name: The original name of the class before mapping
        :type original_name: str
        :param new_name: The new name of the class after mapping
        :type new_name: str
        :param ret_val: The type of the object which is returned by the method
        :type ret_val: str
        :param parameters: The method parameter types
        :type parameters: list of str
        """
        self.original_name = original_name
        self.new_name = new_name
        self.ret_val = ret_val
        self.parameters = parameters


class Class:
    """
    Represents the mapping of a class from the original name of the class
    and its variables and methods to their new name
    """

    def __init__(self, original_name, new_name):
        """
        Class initializer
        :param original_name: The original name of the class before mapping
        :type original_name: str
        :param new_name: The new name of the class after mapping
        :type new_name: str
        """
        self.original_name = original_name
        self.new_name = new_name
        self.methods = {}
        self.vars = {}

    def add_method(self, method):
        """
        Adds a method to the mapping of this class
        :param method: a method in this class
        :type method: Method
        """
        self.methods[method.original_name] = method

    def add_var(self, var):
        """
        Adds a variable to the mapping of this class
        :param var: a variable in this class
        :type var: Variable
        """
        self.vars[var.original_name] = var


class Mapping:
    def __init__(self, mapping):
        """

        :param mapping:
        :type mapping: list of str
        """
        self.classes = {}
        current_class = None
        for line in mapping:
            line = line.rstrip()
            if line.startswith(' '):
                line = line.lstrip()
                if '(' in line:
                    first, new_name = line.split(' -> ')
                    ret_type, meth = first.split(' ')
                    original_name, params = meth.split('(')
                    params = params.replace(')', '').split(',')
                    current_class.add_method(Method(original_name,
                                                    new_name,
                                                    ret_type,
                                                    params))
                else:
                    first, new_name = line.split(' -> ')
                    var_type, original_name = first.split(' ')
                    current_class.add_var(Variable(original_name,
                                                   new_name,
                                                   var_type))
                    pass
            else:
                original_name, new_name = line.split(' -> ')
                current_class = Class(original_name, new_name)
                self.classes[original_name] = current_class
