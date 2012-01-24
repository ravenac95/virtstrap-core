import fudge
from nose.tools import raises
from virtstrap.lib.requirements import (RequirementTranslator, 
        RequirementSpecificationSyntaxError, RequirementScanner,
        RequirementParser)

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
        self.mock_builder = fudge.Fake('builder')
        self.mock_tokenizer = fudge.Fake('tokenizer')
        self.parser = RequirementParser(builder=self.mock_builder,
                tokenizer=self.mock_tokenizer)

    def set_expect_add_condition(self, version, condition):
        self.mock_builder.expects('add_condition').with_args(
                version, condition)

    def set_fake_result(self, result_value):
        self.mock_builder.expects('get_result').returns(result_value)

    def set_tokens(self, tokens):
        self.mock_tokenizer.expects('tokenize').returns(tokens)

    @fudge.test
    def test_parse_simple_requirement(self):
        # builder expects builder.add_condition(version, condition)
        version = '1.3.0'
        condition = '=='
        fake_return = 'fake_return'
        self.set_tokens([
            ('compare', '=='),
            ('version', '1.3.0'),
        ])
        # Expect the builder to call an add condition
        self.set_expect_add_condition(version, condition)
        # Make it return a fake result
        self.set_fake_result(fake_return)
        requirement = self.parser.parse(version)
        assert requirement == fake_return

    @fudge.test
    def test_parse_conditioned_requirement(self):
        version = '1.3.0'
        condition = '>='
        spec = '%s%s' % (condition, version)
        fake_return = 'fake_return'
        self.set_tokens([
            ('compare', '>='),
            ('version', '1.3.0'),
        ])
        self.set_expect_add_condition(version, condition)
        self.set_fake_result(fake_return)
        requirement = self.parser.parse(version)
        assert requirement == fake_return

def test_initialize_scanner():
    scanner = RequirementScanner()

class TestRequirementScanner(object):
    def setup(self):
        self.scanner = RequirementScanner()
    
    def run_scan(self, spec, expected):
        tokens = self.scanner.scan(spec)
        assert tokens == expected

    def test_scan_versions(self):
        tests = [
            '1.2.3',
            '2.3.',
        ]
        for spec in tests:
            expected = [('version', spec)]
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
            expected = [('x_version', spec)]
            yield self.run_scan, spec, expected

    def test_scan_to_operator(self):
        tests = [
            ('0.6.x to 12.3.x', [
                ('x_version', '0.6.x'),
                ('to_operator', 'to'),
                ('x_version', '12.3.x'),
            ]),
            ('10.612.x  to  12.313.x', [
                ('x_version', '10.612.x'),
                ('to_operator', 'to'),
                ('x_version', '12.313.x'),
            ]),
            ('5.0  to  5.4', [
                ('version', '5.0'),
                ('to_operator', 'to'),
                ('version', '5.4'),
            ])
        ]
        for spec, expected in tests:
            yield self.run_scan, spec, expected

    def test_scan_compare_operator(self):
        tests = [
            ('>=1.4.0', [
                ('compare', '>='),
                ('version', '1.4.0'),
            ]),
            ('>=1.2', [
                ('compare', '>='),
                ('version', '1.2'),
            ]),
            ('<=1.2', [
                ('compare', '<='),
                ('version', '1.2'),
            ]),
            ('<1.2', [
                ('compare', '<'),
                ('version', '1.2'),
            ]),
            ('>1.2', [
                ('compare', '>'),
                ('version', '1.2'),
            ]),
            ('>   1.2', [
                ('compare', '>'),
                ('version', '1.2'),
            ]),
            ('==1.2', [
                ('compare', '=='),
                ('version', '1.2'),
            ]),
            ('== 1.2', [
                ('compare', '=='),
                ('version', '1.2'),
            ]),
        ]
        for spec, expected in tests:
            yield self.run_scan, spec, expected


    def test_scan_comma_operator(self):
        tests = [
            ('>1.2,<2.0', [
                ('compare', '>'),
                ('version', '1.2'),
                ('comma', ','),
                ('compare', '<'),
                ('version', '2.0'),
            ]),
            ('>1.2,<2.0,==1.5', [
                ('compare', '>'),
                ('version', '1.2'),
                ('comma', ','),
                ('compare', '<'),
                ('version', '2.0'),
                ('comma', ','),
                ('compare', '=='),
                ('version', '1.5'),
            ]),
            ('> 1.2, < 2.0, == 1.5', [
                ('compare', '>'),
                ('version', '1.2'),
                ('comma', ','),
                ('compare', '<'),
                ('version', '2.0'),
                ('comma', ','),
                ('compare', '=='),
                ('version', '1.5'),
            ]),
        ]
        for spec, expected in tests:
            yield self.run_scan, spec, expected
