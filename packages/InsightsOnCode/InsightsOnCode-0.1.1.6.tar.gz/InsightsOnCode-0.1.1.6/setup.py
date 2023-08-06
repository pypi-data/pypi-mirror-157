from setuptools import setup, find_packages

setup(
    name='InsightsOnCode',
    version='0.1.1.6',
    author='Siddhanth Ramani',
    author_email='dhanth20@gmail.com',
    packages=find_packages(),
    scripts=['bin/sample_easy.py'],
    url='http://pypi.python.org/pypi/InsightsOnCode/',
    license='LICENSE.txt',
    long_description=open('README.txt').read(),
    install_requires=[
        "certifi>=2022.6.15",
        "charset-normalizer>=2.1.0",
        "idna>=3.3",
        "numpy>=1.21.6",
        "pandas>=1.3.5",
        "python-dateutil>=2.8.2",
        "pytz>=2022.1",
        "requests>=2.28.1",
        "six>=1.16.0",
        "urllib3>=1.26.9",
    ],
)