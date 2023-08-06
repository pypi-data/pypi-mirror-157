from setuptools import setup, find_packages


setup(
    name='clasunspsc',
    version='0.3.8',
    license='MIT',
    author="Isaac Zainea",
    author_email='cizaineam@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/ANCP-CCE-Analitica/clas_unspsc',
    keywords='Compra pública, CCE, UNSPSC',
    install_requires=[
          'scikit-learn',
        'numpy',
        'pandas',
        'nltk',
        'spacy',
        'ipywidgets'
      ],

)
