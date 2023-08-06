import setuptools
#from mmp_theme import __version__

# Reads the content of your README.md into a variable to be used in the setup below
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name='mmp_theme',
    version='1.2.1',
    packages=['mmp_theme'],
    license='MIT',
    description='Custom theme and functions for MMP plots',
    long_description=long_description,
    long_description_content_type="text/markdown",  
    author='Giulia Bortolato',
    author_email='giulia.bortolato@milanomultiphysics.com',
    url='https://source.cloud.google.com/mmp-vm/utility_repo/+/master:mmp_theme/',
    install_requires=['requests'],
    
    download_url="https://github.com/giulia-mmp/mmp_theme/archive/refs/tags/v1.2.1.tar.gz"
    
)
