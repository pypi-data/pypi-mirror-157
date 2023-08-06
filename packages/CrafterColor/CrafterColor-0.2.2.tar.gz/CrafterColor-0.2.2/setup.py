from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  "Intended Audience :: Developers",
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
 
setup(
  name='CrafterColor',
  version='0.2.2',
  description='simplest and coolest color Library. print and menaged colors in Python!',
  long_description=open('README.md').read() + '\n\n' + open('CHANGELOG.txt').read(),
  long_description_content_type='text/markdown',
  url='',  
  author='Alawi Hussein Adnan Al Sayegh',
  author_email='programming.laboratorys@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='CrafterColor', 
  packages=find_packages(),
  install_requires=[''] 
)
