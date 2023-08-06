from setuptools import setup

setup(
    name='tremetrics',
    version='0.1.0',
    packages=['tremetrics'],
    url='https://gitlab.com/BCLegon/tremetrics',
    license='MIT',
    author='B.C. Legon',
    author_email='pypi@legon.it',
    description='Tremendous Metrics',
    install_requires=[
        'numpy',
        'pytest',
        'scikit-learn',
    ]
)
