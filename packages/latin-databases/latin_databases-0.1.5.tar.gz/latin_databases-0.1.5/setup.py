
import urllib.request
import requests
from setuptools import setup
from pathlib import Path
from setuptools.command.develop import develop
from setuptools.command.install import install
from latin.bglobals import *

this_directory = Path(__file__).parent
long_description = ( this_directory/ "README.md").read_text()

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        s = 'https://storage.googleapis.com/download/storage/v1/b/deduction4/o/on%20cicero.txt?generation=1656578017964238&alt=media'
        urllib.request.urlopen(s)
        file = f'{fold}hey.txt'
        r = requests.get(s, stream=True, verify=False)
        if r.status_code == 200:
            r.raw.decode_content = 1
            with open(file, 'wb') as f:
                f.write(r.content)
        else:
            p('failed to download data files')

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)

setup(
    name='latin_databases',
    version='0.1.5',
    description='none',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/kylefoley76/latin_databases3',
    author='Kyle Foley',
    author_email='kylefoley202@gmail.com',
    license='BSD',
    zip_safe=False,
    packages=['latin','latin/general_la'],
    install_requires=['Levenshtein',
                      'striprtf==0.0.12',
                      ],
    cmdclass={
            'develop': PostDevelopCommand,
            'install': PostInstallCommand,
        },

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Education',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: MacOS',
        'Programming Language :: Python :: 3.8',
    ],
)

