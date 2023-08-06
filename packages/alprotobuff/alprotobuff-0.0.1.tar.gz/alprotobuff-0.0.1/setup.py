from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: MacOS',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Operating System :: Unix',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='alprotobuff',
  version='0.0.1',
  description='basic test pypi package',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Alok Dadarya',
  author_email='alokd3@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='test test pypi package v1',
  packages=find_packages(),
  install_requires=['protobuf>=3.17.1'],
  python_requires=">=3.6",
  package=['alprotobuff']
)
