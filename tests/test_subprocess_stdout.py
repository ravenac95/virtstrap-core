import fudge
from cStringIO import StringIO
from tests import fixture_path
from virtstrap.lib.caller import (call, SubprocessOutputCollector, 
                    LogOutputStream)

def test_capture_make_output_scripts():
    """Tests both make_output scripts"""
    tests = [
        ('make_output.py', 'abcdef\n', '123456\n'),
        ('make_output2.py', 'ghijkl\n', '789\n'),
    ]
    for filename, alphas, nums in tests:
        yield run_output_stdout, filename, alphas, nums

@fudge.test
def run_output_stdout(filename, alphas, nums):
    """Run output command. For use with generator"""
    fake_output_bin = fixture_path(filename)
    output_stream = fudge.Fake()
    # Expect the make_output.py output
    output_stream.expects('write').with_args(alphas)
    output_stream.next_call().with_args(nums)
    output_stream.next_call().with_args(alphas)
    output_stream.next_call().with_args(nums)

    return_code = call(['python', fake_output_bin], 
            output_stream=output_stream)
    assert return_code == 0
    
@fudge.test
def test_subprocess_output_collector_collects_line():
    """Test the output collector collects a single line"""
    fake_stdout = StringIO()
    fake_stdout.write('hello')
    fake_stdout.seek(0)
    fake_output_stream = fudge.Fake()
    fake_output_stream.expects('write').with_args("hello")
    collector = SubprocessOutputCollector(stdout=fake_stdout,
            output_stream=fake_output_stream)
    collector.collect()

@fudge.test
def test_subprocess_output_collector_collects_many_lines():
    """Test the creation of the SubprocessOutputCollector"""
    fake_stdout = StringIO()
    fake_stdout.write('hello\n')
    fake_stdout.write('world\n')
    fake_stdout.seek(0)
    fake_output_stream = fudge.Fake()
    (fake_output_stream.expects('write')
            .with_args('hello\n')
            .next_call()
            .with_args('world\n'))
    collector = SubprocessOutputCollector(stdout=fake_stdout,
            output_stream=fake_output_stream)
    collector.collect()

@fudge.test
def test_log_output_stream():
    """Test that the output stream makes the calls we expect"""
    fake_logger = fudge.Fake()
    fake_logger.expects('info').with_args('hello')
    log_output_stream = LogOutputStream(logger=fake_logger)
    log_output_stream.write('hello')


@fudge.test
def test_log_output_stream_with_different_level():
    """Test that the output stream logs to a different level"""
    fake_logger = fudge.Fake()
    fake_logger.expects('error').with_args('hello')
    log_output_stream = LogOutputStream(level='error', logger=fake_logger)
    log_output_stream.write('hello')

@fudge.patch('virtstrap.lib.caller.virtstrap_logger')
def test_integrated_call(fake_logger):
    """Integrates call, SubprocessOutputCollector, and LogOutputStream"""
    # initialize the fake logger it's the only fake we need
    alphas = 'abcdef'
    nums = '123456'
    fake_logger.expects('info').with_args(alphas)
    fake_logger.next_call().with_args(nums)
    fake_logger.next_call().with_args(alphas)
    fake_logger.next_call().with_args(nums)
    
    fake_output_bin = fixture_path('make_output.py')
    return_code = call(['python', fake_output_bin])

    
