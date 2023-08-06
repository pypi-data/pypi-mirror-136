from setuptools import setup, find_packages


setup(
    name='AquaTools',
    version='1.0',
    license='None',
    author="Aqua Water Labs",
    author_email='aqua.computer.labs@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://pypi/project/aquatools',
    keywords='Tools for python by Aqua Water Labs',
    install_requires=[
          'scikit-learn',
      ],

)