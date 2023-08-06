from setuptools import find_packages, setup
from setuptools import find_namespace_packages

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Education',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3'
]

setup(
    name='pnwcybersec',
    packages=find_packages(),
    version='0.0.2',
    description='A deep learning malware detection module.',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    long_description_content_type='text/x-rst',
    url = '',
    author = 'Ryan Frederick, Joseph Shapiro',
    author_email='freder20@pnw.edu',
    license='Apache License 2.0',
    classifiers=classifiers,
    keywords='Deep Learning, Cyber Security',
    install_requires=['fastai', 'pandas', 'numpy', 'os', 'PIL', 'matplotlib']
)
