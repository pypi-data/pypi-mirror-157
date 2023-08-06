from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  'Intended Audience :: Education',
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='aimluae',
  version='1.0.3',
  description='Artificial Intelligence & Machine Learning UAE',
  long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
  url='',  
  author='Salman Khan',
  author_email='maker57sk@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='', 
  packages=find_packages(),
  install_requires=[''] 
)