from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='WLed-Control',
  version='1.1.0',
  description='A very basic WLed control library',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Kasper H. Larsen',
  author_email='kasperhornlarsen@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='Wled', 
  packages=find_packages(),
  install_requires=['requests', "webcolors"]
)
