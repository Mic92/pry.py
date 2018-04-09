prepare-release:
	rm -rf dist/*
	python setup.py sdist
	python setup.py bdist_wheel --universal

upload-release:
	twine upload dist/*
