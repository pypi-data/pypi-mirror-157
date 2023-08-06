from setuptools import setup
from pkg_resources import parse_requirements 

setup(
    
    name="gpass",
    version='2.0.2',
    url=  'https://gitlab.com/loggerheads-with-binary/gpass/',
    download_url='http://pypi.python.org/pypi/gpass' , 
    description="A flexible and easy to use, terminal based password input utility",
    author="Anna Aniruddh Radhakrishnan",
    author_email = 'dev@aniruddh.ml' , 
    packages=['gpass'],
    package_dir={
        'gpass': '.',
    },
    install_requires= ['colorama' , 'termcolor'],
    exclude_package_data={ 'gpass' : ['./setup.py'] } ,  
    
    project_urls={
        'Documentation': 'https://gitlab.com/loggerheads-with-binary/gpass/README.md',
        'Source': 'https://gitlab.com/loggerheads-with-binary/gpass/',
        'Tracker': 'https://gitlab.com/loggerheads-with-binary/gpass/issues',
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