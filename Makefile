test:
	nosetests -d

# THIS TEST ONLY WORK ON OSX as far as I know
# It defaults to having a timeout of 30 seconds
ptest: 
	nosetests -d --processes=8 --process-timeout=30

quicktest:
	nosetests -a '!slow' -d

quicktest_verbose:
	nosetests -a '!slow' -d -v
