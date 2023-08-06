# Sunpal
A small demo library for a Sunpal application.

### Installation
```
pip install sunpal
```

### Get started
Write here how start

```Python
import sunpal

# configure
sunpal.configure(SUNPAL_API_KEY, SUNPAL_COMPANY)

```

### Run Tests
```
python3 -m unittest -v tests/customers.py
```

### Deploy library
```
# Compile
python3 setup.py sdist bdist_wheel
# Check
twine check dist/*
# Upload
python3 -m twine upload dist/*
```