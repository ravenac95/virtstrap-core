import re

class RequirementSpecificationSyntaxError(Exception):
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

    def parse(self, string):
        builder = self.builder
        tokenizer = self.tokenizer
        # Get tokens
        tokens = tokenizer.tokenize(string)
        
        builder.add_condition(string, '==')
        return builder.get_result()

# Requirement token processors
def x_version(scanner, token):
    return 'x_version', token

def version(scanner, token):
    return 'version', token

def to_operator(scanner, token):
    return 'to_operator', token

def compare_operator(scanner, token):
    return 'compare', token

def comma_operator(scanner, token):
    return 'comma', token

class RequirementScanner(object):
    rules = [
        (r'[0-9]+(\.[0-9]+)*(\.x)+', x_version),
        (r'[0-9]+(\.[0-9]+)*(\.x){0}\.?', version),
        (r'\bto\b', to_operator),
        (r',', comma_operator),
        (r'((>|<)=?)|(==)', compare_operator),
        (r'\s+', None),
    ]
    
    def __init__(self):
        self.scanner = re.Scanner(self.rules)

    def scan(self, requirement):
        tokens, remainder = self.scanner.scan(requirement)
        return tokens
