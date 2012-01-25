import fudge
from nose.tools import raises
from virtstrap.lib.requirements import (RequirementTranslator, 
        RequirementSpecSyntaxError, RequirementScanner,
        RequirementParser, RequirementTokenizer, SymbolTable, 
        Token)

def test_initialize_translator():
    """Test that we can initialize the requirements translator"""
    translator = RequirementTranslator()

class TestRequirementTranslator(object):
    def setup(self):
        self.translator = RequirementTranslator()

    def test_simple_spec(self):
        """Test a version specification that is simply a number"""
        spec = '1.2.1'
        translated_spec = self.translator.translate(spec)
        # Ensure that 1.2.1 translates to ==1.2.1
        assert translated_spec == '==1.2.1'

    def test_simple_conditional_spec(self):
        """Test a version specification that is simply [comparator][number]"""
        tests = [
            ('>1.3', '>1.3'),
            ('>=1.4', '>=1.4'),
            ('<2.0', '<2.0'),
            ('<=2.0', '<=2.0'),
            ('==2.0', '==2.0'),
        ]
        for spec, expected in tests:
            yield self.translate_simple_conditioned_spec, spec, expected

    def translate_simple_conditioned_spec(self, spec, expected):
        translated_spec = self.translator.translate(spec)
        assert translated_spec == expected

def test_initialize_parser():
    parser = RequirementParser()

class TestRequirementParserAlone():
    """Unit tests for requirements parser"""
    def setup(self):
        self.mock_tokenizer = fudge.Fake('tokenizer')
        self.parser = RequirementParser(tokenizer=self.mock_tokenizer)

    def set_tokens(self, tokens):
        fake_end_token = (fudge.Fake('end_token')
                .has_attr(left_binding_power=0)
                .is_a_stub())
        tokens.append(fake_end_token)
        self.mock_tokenizer.expects('tokenize').returns(iter(tokens))

    @fudge.test
    def test_parse_single_token(self):
        # builder expects builder.add_condition(version, condition)
        fake_return = 'fake_return'
        fake_token = (fudge.Fake('token')
                .expects('null_detonation').returns(fake_return))
        self.set_tokens([
            fake_token,
        ])
        requirement = self.parser.parse('')
        assert requirement == fake_return

    @fudge.test
    def test_parse_conditioned_requirement(self):
        fake_return = 'fake_return'
        fake_token1 = (fudge.Fake('token1')
                .expects('null_detonation').returns('left_arg'))
        fake_token2 = (fudge.Fake('token2')
                .expects('left_detonation')
                .with_args('left_arg')
                .returns(fake_return)
                .has_attr(left_binding_power=10))
        self.set_tokens([
            fake_token1,
            fake_token2
        ])
        requirement = self.parser.parse('')
        assert requirement == fake_return

def test_initialize_tokenizer():
    tokenizer = RequirementTokenizer()

class TestRequirementTokenizer(object):
    def setup(self):
        self.mock_scanner = fudge.Fake()
        self.mock_symbol_table = fudge.Fake()
        self.tokenizer = RequirementTokenizer(scanner=self.mock_scanner,
                symbol_table=self.mock_symbol_table)

    @fudge.test
    def test_tokenize_requirement(self):
        self.mock_scanner.expects('scan').returns(([
            ('literal', 'abc'),
        ], ''))
        (self.mock_symbol_table.expects('create_token').with_args(
                'literal', 'abc'))
        for token in self.tokenizer.tokenize(''):
            pass

def test_initialize_symbol_table():
    symbol_table = SymbolTable(None)

class TestSymbolTable(object):
    def setup(self):
        self.mock_parser = fudge.Fake()
        self.symbol_table = SymbolTable(self.mock_parser)

    def test_define_symbol(self):
        TokenClass = self.symbol_table.define_symbol('test', '?', 100)
        assert Token in TokenClass.__bases__
        assert TokenClass.symbol == '?'

    def test_define_literal(self):
        TokenClass = self.symbol_table.define_literal('literal')
        assert Token in TokenClass.__bases__
        assert TokenClass.symbol == 'literal'
        assert 'literal' in self.symbol_table._literals

    def test_create_literal_symbol(self):
        self.symbol_table.define_literal('literal')
        token = self.symbol_table.create_token('literal', '123')
        nd = token.null_detonation()
        assert token.null_detonation().value == '123'
    
    def test_create_binary_operator_symbol(self):
        self.mock_parser.expects('expression').returns('right')
        self.symbol_table.define_binary_operator('bin_operator', '+', 10)
        token = self.symbol_table.create_token('bin_operator', '+')
        left_det_values = token.left_detonation('left')
        assert left_det_values.left == 'left'
        assert left_det_values.right == 'right'

def test_initialize_scanner():
    scanner = RequirementScanner()

class TestRequirementScanner(object):
    def setup(self):
        self.scanner = RequirementScanner()
    
    def run_scan(self, spec, expected):
        tokens, remainder = self.scanner.scan(spec)
        assert tokens == expected
        assert remainder == ''

    def test_scan_versions(self):
        tests = [
            '1.2.3',
            '2.3.',
        ]
        for spec in tests:
            expected = [('VERSION', spec)]
            yield self.run_scan, spec, expected

    def test_scan_x_version(self):
        tests = [
            '0.6.x',
            '10.15.x',
            '1000.14.x',
            '2.0.x',
            '1.x',
            '0.x.x',
        ]
        for spec in tests:
            expected = [('X_VERSION', spec)]
            yield self.run_scan, spec, expected

    def test_scan_to_operator(self):
        tests = [
            ('0.6.x to 12.3.x', [
                ('X_VERSION', '0.6.x'),
                ('bin_operator', 'to'),
                ('X_VERSION', '12.3.x'),
            ]),
            ('10.612.x  to  12.313.x', [
                ('X_VERSION', '10.612.x'),
                ('bin_operator', 'to'),
                ('X_VERSION', '12.313.x'),
            ]),
            ('5.0  to  5.4', [
                ('VERSION', '5.0'),
                ('bin_operator', 'to'),
                ('VERSION', '5.4'),
            ])
        ]
        for spec, expected in tests:
            yield self.run_scan, spec, expected

    def test_scan_compare_operator(self):
        tests = [
            ('>=1.4.0', [
                ('compare', '>='),
                ('VERSION', '1.4.0'),
            ]),
            ('>=1.2', [
                ('compare', '>='),
                ('VERSION', '1.2'),
            ]),
            ('<=1.2', [
                ('compare', '<='),
                ('VERSION', '1.2'),
            ]),
            ('<1.2', [
                ('compare', '<'),
                ('VERSION', '1.2'),
            ]),
            ('>1.2', [
                ('compare', '>'),
                ('VERSION', '1.2'),
            ]),
            ('>   1.2', [
                ('compare', '>'),
                ('VERSION', '1.2'),
            ]),
            ('==1.2', [
                ('compare', '=='),
                ('VERSION', '1.2'),
            ]),
            ('== 1.2', [
                ('compare', '=='),
                ('VERSION', '1.2'),
            ]),
        ]
        for spec, expected in tests:
            yield self.run_scan, spec, expected


    def test_scan_comma_operator(self):
        tests = [
            ('>1.2,<2.0', [
                ('compare', '>'),
                ('VERSION', '1.2'),
                ('bin_operator', ','),
                ('compare', '<'),
                ('VERSION', '2.0'),
            ]),
            ('>1.2,<2.0,==1.5', [
                ('compare', '>'),
                ('VERSION', '1.2'),
                ('bin_operator', ','),
                ('compare', '<'),
                ('VERSION', '2.0'),
                ('bin_operator', ','),
                ('compare', '=='),
                ('VERSION', '1.5'),
            ]),
            ('> 1.2, < 2.0, == 1.5', [
                ('compare', '>'),
                ('VERSION', '1.2'),
                ('bin_operator', ','),
                ('compare', '<'),
                ('VERSION', '2.0'),
                ('bin_operator', ','),
                ('compare', '=='),
                ('VERSION', '1.5'),
            ]),
        ]
        for spec, expected in tests:
            yield self.run_scan, spec, expected
