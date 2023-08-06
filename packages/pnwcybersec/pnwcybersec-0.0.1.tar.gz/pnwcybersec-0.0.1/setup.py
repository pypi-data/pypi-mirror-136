from setuptools import setup, find_packages
from distutils.core import setup

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Education',
    ' License :: OSI Approved :: Apache Software License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3'
]

setup(
    name='pnwcybersec',
    version='0.0.1',
    description='A deep learning malware detection module.',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url = '',
    author = 'Ryan Frederick, Joseph Shapiro',
    author_email='freder20@pnw.edu',
    license='Apache License 2.0',
    classifiers=classifiers,
    keywords=['Deep Learning', 'Cyber Security'],
    packages=find_packages(),
    #install_requirements=['fastai', 'pandas', 'numpy', 'os', 'PIL', 'matplotlib']
)
