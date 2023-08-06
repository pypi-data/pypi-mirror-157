from setuptools import setup, find_packages
 
classifiers = [
  'Development Status :: 5 - Production/Stable',
  "Intended Audience :: Developers",
  'Operating System :: Microsoft :: Windows :: Windows 10',
  'Operating System :: POSIX',
  'License :: OSI Approved :: MIT License',
  'Programming Language :: Python :: 3'
]
__description__ = '''a Personal package for me.  automatically append paths to sys.path.  mange sys.path package.'''
setup(
  name='PYPATHER',
  version='0.0.3',
  description=__description__,
  long_description=open('README.md').read(),
  long_description_content_type='text/markdown',
  url='',  
  author='Alawi Hussein Adnan Al Sayegh',
  author_email='programming.laboratorys@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='PYPATHER', 
  packages=find_packages(),
  install_requires=[] 
)