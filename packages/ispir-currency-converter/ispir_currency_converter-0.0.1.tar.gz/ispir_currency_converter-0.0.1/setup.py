from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Currency converter python package'
LONG_DESCRIPTION = 'Currency converter python package'

setup(
    name='ispir_currency_converter',                     # package name
    author='Igor Ispir',
    author_email='ispir.igor@gmail.com',
    version=VERSION,                                   # version
    description=DESCRIPTION,                           # short description
    long_description=LONG_DESCRIPTION,
    url='https://gitlab.com/igorfortestnc/currency-converter.git', # package URL
    install_requires=[],                               # list of packages this package depends
                                                       # on.
    packages=find_packages(),                          # List of module names that installing
                                                       # this package will provide.
    keywords=['python', 'ispir_currency_converter'],
)
