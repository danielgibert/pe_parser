from setuptools import setup, find_packages
requires = ['nltk', 'mahotas', 'matplotlib']

setup(name='pe_parser',
      version='0.1',
      description='PE parser implementation',
      url='https://github.com/danielgibert/pe_parser',
      author='Daniel Gibert',
      author_email='danigibert24@gmail.com',
      license='MIT',
      packages=['pe_parser'],
      package_data={"pe_parser":["vocabulary/*.txt", "vocabulary/*.json", "*.md"]},
      install_requires=requires,
      zip_safe=False,
      install_package_data=True,
      python_requires='>=3.6.9'
      )
