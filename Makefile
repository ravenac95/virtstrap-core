test:
	nosetests -d

quicktest:
	nosetests -a '!slow' -d

quicktest_verbose:
	nosetests -a '!slow' -d -v
