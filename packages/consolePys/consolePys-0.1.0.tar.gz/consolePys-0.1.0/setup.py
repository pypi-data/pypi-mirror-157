from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  "Intended Audience :: Developers",
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Operating System :: POSIX',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]

setup(
  name='consolePys',
  version='0.1.0',
  description='easy tool for ColorCraft, some Features',
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  url='',  
  author='Alawi Hussein Adnan Al Sayegh',
  author_email='programming.laboratorys@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='PyConsole, Console, ConsolePy, consolePys, ConsolePys', 
  packages=find_packages(),
  install_requires=['ColorCraft'] 
)