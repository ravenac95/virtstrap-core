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
    def __init__(self, tokenizer=None):
        self.tokenizer = tokenizer
        self._token = None
        self._next_token = None

    def parse(self, requirement):
        tokenizer = self.tokenizer
        # Get tokens
        token_iter = tokenizer.tokenize(requirement)
        self._next_token = token_iter.next
        self._token = token_iter.next()
        return self.expression()

    def expression(self, right_binding_power=0):
        """Internal parsing mechanism"""
        current_token = self._token
        next_token = self._next_token
        left = current_token.null_detonation(self)
        token = next_token()
        while right_binding_power < token.left_binding_power:
            current_token = token
            token = next_token()
            left = current_token.left_detonation(left)
        return left

class Token(object):
    symbol = None
    value = None

    def __init__(self, parser):
        self.parser = parser

    def null_detonation(self):
        raise RequirementSpecSyntaxError('Syntax error (%r).' % self.symbol)

    def left_detonation(self, left):
        raise RequirementSpecSyntaxError('Unknown operator '
                '(%r).' % self.symbol)

# FIXME this could be done much better
class SymbolTable(object):
    def __init__(self, parser):
        self._symbol_table = {}
        self._literals = []
        self.parser = parser

    def define_symbol(self, token_type, symbol, binding_power=0):
        """Generate a new symbol given the options above"""
        symbol_table = self._symbol_table
        try:
            TokenClass = symbol_table[symbol]
        except KeyError:
            class TokenClass(Token):
                pass
            TokenClass.__name__ = "symbol-%s" % symbol
            TokenClass.symbol = symbol
            TokenClass.left_binding_power = binding_power
            symbol_table[symbol] = TokenClass
        else:
            current_binding_power = TokenClass.left_binding_power 
            TokenClass.left_binding_power = max(binding_power, 
                    current_binding_power)
        return TokenClass

    def define_binary_operator(self, token_type, symbol, binding_power):
        def left_detonation(self, left):
            self.left = left
            self.right = self.parser.expression(binding_power)
            return self
        TokenClass = self.define_symbol(token_type, symbol, binding_power)
        TokenClass.left_detonation = left_detonation
        return TokenClass

    def define_unary_operator(self, token_type, symbol, binding_power, 
            position="left"):
        TokenClass = self.define_symbol(token_type, symbol, binding_power)
        if position == "left":
            # if the operator is on the left like -1 or not 2 then use
            # null detonation
            def null_detonation(self, left):
                self.left = None
                self.right = self.parser.expression(binding_power)
                return self
            TokenClass.left_detonation = left_detonation
        else:
            def left_detonation(self, left):
                self.left = left
                self.right = None
                return self
            TokenClass.null_detonation = null_detonation
        return TokenClass

    def define_literal(self, token_type):
        TokenClass = self.define_symbol(token_type, token_type)
        def null_detonation(self):
            return self
        TokenClass.null_detonation = null_detonation
        self._literals.append(token_type)
        return TokenClass

    def create_token(self, token_type, symbol):
        if token_type in self._literals:
            TokenClass = self._symbol_table.get(token_type)
            token = TokenClass(self.parser)
            token.value = symbol
            return token
        TokenClass = self._symbol_table.get(symbol)
        if not TokenClass:
            raise RequirementSpecSyntaxError('Unknown operator "%s"' % token)
        token = TokenClass(self.parser)
        return token
    
class RequirementTokenizer(object):
    def __init__(self, scanner=None, symbol_table=None):
        self.scanner = scanner
        self.symbol_table = symbol_table

    def tokenize(self, requirement):
        """Maps data from scanner into objects"""
        tokens, remainder = self.scanner.scan(requirement)
        for token_type, symbol in tokens:
            yield self.symbol_table.create_token(token_type, symbol)

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
        (r'((>|<|!)=?)|(==)', compare_operator),
        (r'\s+', None),
    ]
    
    def __init__(self):
        self.scanner = re.Scanner(self.rules)

    def scan(self, requirement):
        return self.scanner.scan(requirement)
