from distutils.core import setup

setup(
  # Application name:
  name="pythonmachineid",

  # Version number (initial):
  version="0.0.1.dev1",

  # Application author details:
  author="Ernest Offiong",
  author_email="ernest.offiong@gmail.com",

  # Packages
  packages=["pythonmachineid"],

  # Include additional files into the package
  include_package_data=True,

  # Details
  url="http://pypi.python.org/pypi/pythonmachineid_v001.dev1/",

  license="MIT",
  python_requires='>=3',
  description="Python Machine Id library",

  # long_description=open("README.txt").read(),

  # Dependent packages (distributions)
  install_requires=[
    "pycryptodome"
  ],

  classifiers=[
    # 'Development Status :: 3 - Alpha',   
    'Intended Audience :: Developers',     
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',  
    'Programming Language :: Python :: 3',      
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],

)