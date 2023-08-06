# Quick-PyPI

The simplest and quickest way to build and upload a PyPI package

## Installation
```pip
pip install quick-pypi
```

## Minimum Example

Before you start, you need to have several things:
- Determine a unique PyPI package name, easy to remember, like 'quick-pypi-test';
- Have a PyPI account, then export your upload token to a txt file in your computer;
- Use PyCharm IDE to develop your own package. NOT notebook!

Step 1: Prepare your PyCharm project tree like:
```
PyCharm Project Root
 -- src
   -- your_package_name
     -- __init__.py
     -- your_class.py   # where you can write your own code!
 -- dists               # auto generated folder storing uploading version history
   -- 0.0.1
   -- 0.0.2
   -- ...
   -- VERSION           # a file storing the latest version of uploading
 quick-pypi.py          # Main settings of uploading package
```

Step 2: The simplest `quick-pypi.py` file content is below: 
```python
from quick_pypi.deploy import *
auto_deploy(
    cwd=os.path.dirname(os.path.realpath(__file__)), # current working directory, generally as project root
    name="quick-pypi-test",
    description="This is a quick-pypi-test package!",
    pypi_token='../../pypi_upload_token.txt', # the token string or path from your PyPI account
)
```

Step 3: Deploy the package to PyPI server

After you finish writing your codes in the `src` package, you can just simply right-click the `quick-pypi.py` to run, and wait for its completion.

Step 4: Check if the package is uploaded successfully!

## Complicated Example settings for advanced users

```python
from quick_pypi.deploy import *
auto_deploy(
    cwd=os.path.dirname(os.path.realpath(__file__)),
    name="quick-pypi-test",
    long_name="Quick Pypi Test Package",
    description="This is a quick-pypi-test package!",
    long_description="This is a long description!",
    src_root="src",
    dists_root=f"dists",
    pypi_token='../../pypi_upload_token.txt', # a file storing the token from your PyPI account
    test=False, # determine if uploading to test.pypi.org
    version="0.0.1a0", # fixed version when uploading or using version='auto'
    project_url="http://github.com/dhchenx/quick-pypi",
    author_name="Donghua Chen",
    author_email="xxx@xxx.com",
    requires="jieba;quick-crawler",
    license='MIT',
    license_filename='LICENSE',
    github_username="dhchenx",
    keywords="quick,pypi,deploy",
)
```
Here you can provide more information about your package, like setting your author's name, email, license, short or long names and descriptions, etc. 


## License
The `quick-pypi` project is provided by [Donghua Chen](https://github.com/dhchenx). 

