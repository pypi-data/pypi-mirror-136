# Build currency package:

First, install package **pip install twine**

Build package command: **python3 setup.py sdist bdist_wheel**

Upload to pypi.org: **twine upload dist/***


After: **pip install isp-currency-converter==0.0.1**