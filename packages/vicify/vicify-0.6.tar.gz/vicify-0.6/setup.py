from setuptools import setup, find_packages


setup(
    name='vicify',
    version='0.6',
    license='MIT',
    author="Mohammed Saifullah",
    author_email='isaeefulla@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/humblefool1997/vicify',
    keywords='vcf convertor',
    install_requires=[
          'pandas',
      ],

)
