from setuptools import setup
from setuptools import find_packages

setup(
    name='metacritic_scraper', ## This will be the name your package will be published with
    version='1.0.0', 
    description='Test package that scrapes',
    # url='https://github.com/IvanYingX/project_structure_pypi.git', # Add the URL of your github repo if published 
                                                                   # in GitHub
    author='Wayne Rose', # Your name
    license='GNU General Public License',
    packages=find_packages(), 
    install_requires=['webdriver_manager', 'selenium', 'pandas', 'numpy', 'boto3'], # The external libraries 
                                                     
)