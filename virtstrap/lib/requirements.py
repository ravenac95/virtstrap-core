import re

class RequirementSpecSyntaxError(Exception):
    pass

class RequirementTranslator(object):
    def translate(self, requirement):
        comparators = ['==', '>=', '>', '<', '<=']
        for comparator in comparators:
            if requirement.startswith(comparator):
                return requirement
        return "==" + requirement

class RequirementParser(object):
    def __init__(self, builder=None, tokenizer=None):
        self.builder = builder
        self.tokenizer = tokenizer
        self._token = None
        self._next_token = None

    def parse(self, requirement):
        builder = self.builder
        tokenizer = self.tokenizer
        # Get tokens
        tokens = tokenizer.tokenize(requirement)
        #token_iter = map(lambda token, name: types[token](builder), tokens)

        builder.add_condition(requirement, '==')
        return builder.get_result()

    def expression(self, right_binding_power=0):
        """Internal parsing mechanism"""
        current_token = self._token
        next_token = self._next_token
        token = next_token()
        left = current_token.null_det(self)
        while right_binding_power < token.left_binding_power:
            current_token = token
            token = next_token()
            left = current_token.left_det(left, self)
        return left

class Token(object):
    id = None
    value = None

    def null_detonation(self):
        raise RequirementSpecSyntaxError('Syntax error (%r).' % self.name)

    def left_detonation(self):
        raise RequirementSpecSyntaxError('Unknown operator (%r).' % self.name)

class TokenTable(object):
    def __init__(self):
        self._symbol_table = {}
        self._literals = []

    def define_symbol(self, token_type, id, binding_power=0):
        """Generate a new token given the options above"""
        symbol_table = self._symbol_table
        try:
            TokenClass = symbol_table[id]
        except KeyError:
            class TokenClass(Token):
                pass
            TokenClass.__name__ = "symbol-%s" % id
            TokenClass.id = id
            TokenClass.left_binding_power = binding_power
            symbol_table[id] = TokenClass
        else:
            current_binding_power = TokenClass.left_binding_power 
            TokenClass.left_binding_power = max(binding_power, 
                    current_binding_power)
        return TokenClass

    def define_literal(self, token_type):
        self.define_symbol(token_type, token_type)
        self._literals.append(token_type)

    def create_token(self, token_type, token):
        symbol = self._symbol_table.get(literal_symbol)
        if token_type in self._literals:
            symbol_instance = symbol()
            symbol_instance.value = token
            return symbol_instance
        if not symbol:
            raise RequirementSpecSyntaxError('Unknown operator "%s"' % token)
        return symbol()

class RequirementTokenizer(object):
    def __init__(self, scanner=None, token_table=None):
        self.scanner = scanner
        self.token_table = token_table

    def tokenize(self, requirement):
        """Maps data from scanner into objects"""
        tokens, remainder = self.scanner.scan(requirement)
        for token_type, token in tokens:
            yield self.token_table.create_token(token_type, token)

# Requirement token processors
def version(scanner, token):
    return 'VERSION', token

def x_version(scanner, token):
    return 'X_VERSION', token

def bin_operator(scanner, token):
    return 'bin_operator', token

def compare_operator(scanner, token):
    return 'compare', token

def comma_operator(scanner, token):
    return 'bin_operator', token

class RequirementScanner(object):
    rules = [
        (r'[0-9]+(\.[0-9]+)*(\.x)+', x_version),
        (r'[0-9]+(\.[0-9]+)*(\.x){0}\.?', version),
        (r'\bto\b', bin_operator),
        (r',', comma_operator),
        (r'((>|<)=?)|(==)', compare_operator),
        (r'\s+', None),
    ]
    
    def __init__(self):
        self.scanner = re.Scanner(self.rules)

    def scan(self, requirement):
        return self.scanner.scan(requirement)
