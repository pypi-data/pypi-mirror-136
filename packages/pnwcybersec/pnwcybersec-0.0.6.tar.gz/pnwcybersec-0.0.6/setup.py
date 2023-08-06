from setuptools import find_packages, setup
from setuptools import find_namespace_packages

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Education',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
]

setup(
    name='pnwcybersec',
    packages=find_packages(),
    version='0.0.6',
    description='A deep learning malware detection module.',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    long_description_content_type='text/markdown',
    url = 'https://github.com/bbdcmf/pnwcybersec',
    download_url = 'https://github.com/bbdcmf/pnwcybersec/archive/refs/tags/v0.0.3.tar.gz',
    project_urls={
        "Bug Tracker": "https://github.com/bbdcmf/pnwcybersec/issues",
    },
    author = 'Ryan Frederick, Joseph Shapiro',
    author_email='freder20@pnw.edu',
    license='Apache License 2.0',
    classifiers=classifiers,
    keywords='Deep Learning, Cyber Security',
    install_requires=['fastai', 'pandas', 'numpy', 'PIL', 'matplotlib']
)
