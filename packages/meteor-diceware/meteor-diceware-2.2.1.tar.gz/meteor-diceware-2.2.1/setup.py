from setuptools import setup
from pkg_resources import parse_requirements 

setup(
    
    name="meteor-diceware",
    version='2.2.1',
    url=  'https://gitlab.com/loggerheads-with-binary/meteor-diceware/',
    download_url='http://pypi.python.org/pypi/meteor-diceware' , 
    description="A low-resource, easy to use, low latency, customizable and cryptographically secure implementation of Diceware",
    author="Anna Aniruddh Radhakrishnan",
    author_email = 'dev@aniruddh.ml' , 
    packages=['meteor_diceware'],
    package_dir={
        'meteor_diceware': '.',
    },
    install_requires= open('requirements.txt' , 'r' , encoding = 'utf8').readlines(),
    
    package_data = {'meteor_diceware' : [   './init.sql' , './actual_diceware.txt' , './default.sqlite3' , 
                                            './snowflake.md'  , './snowflake.pdf' , 
                                            ]} , 
    
    exclude_package_data={ 'meteor_diceware' : ['./dicecalls.proc.py' , './setup.py'] } ,  
    
    project_urls={
        'Documentation': 'https://gitlab.com/loggerheads-with-binary/meteor-diceware/README.md',
        'Source': 'https://gitlab.com/loggerheads-with-binary/meteor-diceware/',
        'Tracker': 'https://gitlab.com/loggerheads-with-binary/meteor-diceware/issues',
    },
    
    classifiers=[   
            'Operating System :: OS Independent' ,
            "Environment :: Console" , 
            'Intended Audience :: Developers',
            "Intended Audience :: System Administrators" , 
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3',
            "Natural Language :: English" , 
            "Programming Language :: PL/SQL" , 
            'Topic :: Security :: Cryptography' , 
    ], 
 
    long_description_content_type='text/markdown',
    long_description=open('README.md').read()
)