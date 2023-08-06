## Setting up a new project

1. Change version number
2. Run 
    `python setup.py sdist`
3. Run 
    `twine upload --repository-url https://upload.pypi.org/legacy/ dist/*`

## Setting up test and live PyPi environments
```
sudo nano ~/.pypirc

[distutils]
index-servers =
  pypi
  pypitest
  testpypi

[pypi]
repository: https://upload.pypi.org/legacy/
username = markgacoka

[pypitest]
repository: https://test.pypi.org/legacy/
username = markgacoka

[testpypi]
username = markgacoka
```

### Test: 
```
python setup.py sdist bdist
python setup.py register -r pypitest
python setup.py sdist upload -r pypitest

twine upload --repository testpypi dist/*
```

### Live:
```
python setup.py sdist
twine upload dist/*

python setup.py register -r pypi
python setup.py sdist upload -r pypi
```