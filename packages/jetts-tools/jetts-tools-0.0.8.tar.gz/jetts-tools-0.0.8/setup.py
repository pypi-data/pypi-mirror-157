from setuptools import setup, find_packages

with open('README.md') as f:
    readme = f.read()

setup(
    name='jetts-tools',
    version='0.0.8',
    author='Jett Crowson',
    author_email='jettcrowson@gmail.com',
    url='https://github.com/jettdc/jetts-tools',
    description='Various useful python utility functions.',
    long_description=readme,
    long_description_content_type='text/markdown',
    license='MIT',
    packages=['jettools'],
    keywords='python tools utils',
    python_requires='>=3.5'
)
