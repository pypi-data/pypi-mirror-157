from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Developers',
  'Operating System :: MacOS',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='consolelogcmd',
  version='0.0.1',
  description='A Very Simple Console Log Command',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='GalaxyDevel0per',
  author_email='galaxydevel0per@duck.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='calculator, console, log, command', 
  packages=find_packages(),
  install_requires=[''] 
)