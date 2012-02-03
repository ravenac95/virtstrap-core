test:
	nosetests -d

quicktest:
	nosetests -a '!slow' -d
