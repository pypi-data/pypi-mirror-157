from setuptools import setup
import os 

os.chdir(os.path.dirname(os.path.abspath(__file__)))

setup(
    
    name="jihyocrypt",
    version='2.5.0',
    url=  'https://gitlab.com/loggerheads-with-binary/jihyocrypt/',
    download_url='http://pypi.python.org/pypi/jihyocrypt' , 
    description="A simple implementation of Salsa20 along with a nonce+password based key and hash determination function. \
    Multiple exposed functions to ease encryption and decryption to a single key based program. ",
    author="Anna Aniruddh Radhakrishnan",
    author_email = 'dev@aniruddh.ml' , 
    packages=['jihyocrypt'],
    package_dir={
        'jihyocrypt': '.',
    },
    
    install_requires = ['pycryptodome' ],
    
    package_data = {'jihyocrypt' : ['./README.md']} , 
    
    exclude_package_data={ 'jihyocrypt' : ['./__main__.py' , './getpass.py' , './setup.py' , './speedtests.py'] } ,  
    
    project_urls={
        'Documentation': 'https://gitlab.com/loggerheads-with-binary/jihyocrypt/README.md',
        'Source': 'https://gitlab.com/loggerheads-with-binary/jihyocrypt/',
        'Tracker': 'https://gitlab.com/loggerheads-with-binary/jihyocrypt/issues',
    },
    
    classifiers=[   
            'Operating System :: OS Independent' ,
            "Environment :: Console" , 
            'Intended Audience :: Developers',
            "Intended Audience :: System Administrators" , 
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            "Natural Language :: English" ,  
            'Topic :: Security :: Cryptography' , 
    ], 
 
    long_description_content_type='text/markdown',
    long_description=open('README.md').read()
)