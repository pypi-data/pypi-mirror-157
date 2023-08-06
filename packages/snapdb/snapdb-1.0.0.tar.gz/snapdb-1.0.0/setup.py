import setuptools
from snapdb.version import Version


setuptools.setup(name='snapdb',
                 version=Version('1.0.0').number,
                 description='Python adapter for SnapDB',
                 long_description=open('README.md').read().strip(),
                 author='Scott Cruwys',
                 author_email='scruwys@gmail.com',
                 url='https://github.com/scruwys/snapdb-python',
                 py_modules=['snapdb'],
                 install_requires=[],
                 license='MIT License',
                 zip_safe=False,
                 keywords='snapdb',
                 classifiers=['Development Status :: 1 - Planning', 'License :: OSI Approved :: MIT License'])
