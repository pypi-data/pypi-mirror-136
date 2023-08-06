from setuptools import setup, find_packages
 
classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Education',
    'Operating System :: Microsoft :: Windows :: Windows 10',
    'License :: OSI Approved :: MIT License',
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
]

# classifiers=[
#         "Development Status :: 4 - Beta",
#         "Environment :: Console",
#         "License :: OSI Approved :: MIT License",
#         "Programming Language :: Python :: 2.7",
#         "Programming Language :: Python :: 3",
#         "Programming Language :: Python :: 3.5",
#         "Programming Language :: Python :: 3.6",
#         "Programming Language :: Python :: 3.7",
#         "Programming Language :: Python :: 3.8",
#         "Programming Language :: Python :: 3.9",
#         "Intended Audience :: Developers",
#         "Operating System :: OS Independent",
#         "Programming Language :: Python :: Implementation :: CPython",
#         "Programming Language :: Python :: Implementation :: PyPy",
#         "Topic :: Utilities",
#     ],
 
setup(
  name='check_digit_EAN13',
  version='0.1',
  description='A simple library to get check digit',
  long_description=open('README.rst').read(),
  url='',  
  author='Muhammed gassali',
  author_email='mhdgassalishalu5554@gmail.com',
  license='MIT', 
  classifiers=classifiers,
  keywords='check-digit', 
  packages=find_packages(),
  install_requires=[''] 
)