from setuptools import setup, find_packages
from pathlib import Path

readme = """# Binubuo

**Binubuo** is a simple and powerful client to the Binubuo API. The API is used to generate fake or synthetic data that is realistic.
```python
>>> from binubuo import binubuo
>>> b = binubuo('<RapidAPI key>')
>>> print(b.generate('person', 'full_name'))
Andrew Howard
>>> print(b.generate('finance', 'bank_account_id'))
GE02Pu5783332775138823
>>> print(b.generate('consumer', 'food_item'))
Pumpkin Spice, Atlantic Salmon, 2 Bonless Fillets
>>> print(b.generate('time', 'date'))
1945-02-10T17:37:09Z
```

The Binubuo API has more than 150+ real life data generators, across 10+ data domains such as person, finance, computer, investment and many more. For full details on what type
of data Binubuo can generate and uder which domains, you can see the full list here: https://binubuo.com/ords/r/binubuo_ui/binubuo/documentation-generators

To use the python client, you need an API key from RapidAPI. If you do not have an account with RapidAPI, you can create one here: https://rapidapi.com/auth/sign-up.
Once you have signed up, go to the Binubuo page, and choose the plan that fits you (free plan available): https://rapidapi.com/codemonth/api/binubuo/pricing.
You can also play around and test all the generators at: https://rapidapi.com/codemonth/api/binubuo/

## Installing Binubuo client and supported versions

Binubuo is available and installable from PyPI:

    $ python -m pip install binubuo

Binubuo officially supports Python 2.7 & 3.6+.

## Features and Examples

### Getting multiple generator values in one call

**Binubuo** defaults to only give you one result when you call a generator, but there are times when we need more than one result. For that you can simply
specify the number of results you want, and then a list of results instead of a single value is returned to you.

```python
>>> from binubuo import binubuo
>>> b = binubuo('<RapidAPI key>')
>>> print(b.generate('person', 'full_name'))
Addison Watson
>>> b.grows(5) # Set the values count to 5
>>> mylist = b.generate('person', 'full_name')
>>> print(*mylist, sep = "\\n")
Molly King
Charles Phillips
Logan Jackson
David Patterson
Bentley Garcia
```

### "Repeatable" random values

**Binubuo** has a feature called repeatable random. What this feature does, is that it allows you to generate the same random data again, without
persisting the data anywhere in between. This feature is extremely usefull for doing same tests over and over again, with the same test data. Simply "tag"
your data, and you can always go back and get it again.

```python
>>> from binubuo import binubuo
>>> b = binubuo('<RapidAPI key>')
>>> b.grows(3)
>>> b.tag('For test A31') # Tag the data
>>> mylist = b.generate('person', 'full_name')
>>> print(*mylist, sep = "\\n")
Caleb Barnes
Daniel Reed
Faith Adams
>>> b.tag() # Reset to empty tag to get new rows.
>>> mylist = b.generate('person', 'full_name')
>>> print(*mylist, sep = "\\n")
Grayson James
Landon Garcia
Makayla Hughes
>>> b.tag('For test A31') # Set the tag back, to generate same rows
>>> mylist = b.generate('person', 'full_name')
>>> print(*mylist, sep = "\\n")
Caleb Barnes
Daniel Reed
Faith Adams
```

### Different locales supported

**Binubuo** supports generating data according to specific locales. For a list of generators and supported locales, see the generator documentation. 
More and more locales are being added every month. The following example shows how to set the locale and swithc it back to default again, as well
as showing that both two letter ISO codes and full names are supported.

```python
>>> from binubuo import binubuo
>>> b = binubuo('<RapidAPI key>')
>>> print(b.generate('person', 'full_name'))
Khloe Bennett
>>> b.locale('DK') # Set the locale to Denmark
>>> print(b.generate('person', 'full_name'))
Freja Jeppesen
>>> print(b.generate('location', 'city'))
Tønder
>>> print(b.generate('finance', 'bank_account_id'))
DK4883897675725594
>>> b.locale('China') # Set the locale to China
>>> print(b.generate('person', 'full_name'))
Cheng Fù
>>> print(b.generate('location', 'city'))
扬州市
>>> b.locale() # Reset back to default (US)
>>> print(b.generate('person', 'full_name'))
Blake Peterson
>>> print(b.generate('location', 'city'))
Fontana
```

## Data Features

**Binubuo** supports many data domains and data generators. The below list is just a few examples. Look here for the full list: https://binubuo.com/ords/r/binubuo_ui/binubuo/documentation-generators

* Basic
    * Natural
    * Integer
    * Float
* Business
    * Industry
    * Company Name
* Computer
    * Email
    * Url
    * File Name
    * ipv6
    * Domain Name
* Consumer
    * Food Item
    * Nonfood Item
* Finance
    * Credit Card Number
    * Account Transaction
    * Bank Account ID
    * Transaction Status
* Games
    * Coin Toss
    * Dice Roll
* Investment
    * Fund Name
    * ISIN
    * Swift ID
    * Risk Rating
* Location
    * City
    * Zipcode
    * Address
    * Street Name
* Logistics
    * BIC
    * Container Number
    * Shipping Company
* Medical
    * ICD10
* Person
    * Full name
    * Age
    * Job Title
    * Personal ID
* Phone
    * Phone Number
    * MEID
    * IMSI
    * IMEI
    * Operator Code
* Science
    * Chemical Element
    * Scale
    * Tree
    * Planet
* Text
    * Word
    * Adjective
    * Sentence
* Time
    * Date
    * Day
    * Epoch
    * Timestamp
* Transport
    * License Plate
    * ICAO
    * IMO
"""

packages = ['binubuo']

requires = [
    'requests>=2.0.0; python_version >= "3"'
]

setup(
    name='binubuo',
    version='0.0.4',
    description='Client package for Binubuo synthetic data generator',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://binubuo.com',
    author='Morten',
    author_email='morten@binubuo.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',
        'Environment :: Web Environment',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development',
        'Topic :: Software Development :: Testing :: Mocking',
        'Topic :: Utilities',
    ],
    keywords='synthetic, testdata, mocking',
    packages=packages,
    package_dir={'binubuo': 'binubuo'},
    install_requires=requires,
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*',
    project_urls={  # Optional
        'Bug Reports': 'https://github.com/morten-egan/binubuo-python-client/issues/new'
    },
)