from setuptools import setup

setup_args = {
   'description': 'Testing...',
   'author': 'Daniel Ingraham',
   'author_email': 'd.j.ingraham@gmail.com',
   'install_requires': ['juliapkg', 'juliacall'],
   'url': 'https://github.com/dingraha/pyfoo',
   'license': 'MIT',
   'name': 'pyfoo',
   'packages': ['pyfoo'],
   'version': '0.1.3',
   'include_package_data': True}

setup(**setup_args)
