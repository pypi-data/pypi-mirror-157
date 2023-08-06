# ODM2DataModels

## What is this?
odm2datamodels is a Python package that provides a set of object-relational mapping (ORM) data models for the [Observations Data Model Version 2.1](http://www.odm2.org/). This data models are built of the [SQLAlchemy](https://www.sqlalchemy.org/) and provide a convenient way of interfacing with an ODM2.1 database. 

## Core Features
The primary is the `ODM2DataModels` class, which once instantiated, provides access to the set of ORM ODM2.1 data models and an instance of an ODM2Engine which provide utility function to perform basic Create, Read, Update, Delete operations as well are read execution of custom SQLQueries constructed using a SQLAlchemy [Select object](https://docs.sqlalchemy.org/en/14/orm/queryguide.html#select-statements) or [Query Object](https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query)     

## How to install?
Presently the build files are only available on our [github repository](https://github.com/ODM2/ODM2DataModels) 

Though we are aiming to release to the [Python Package Index (PyPI)](https://pypi.org/) and [Conda](https://docs.conda.io/en/latest/) in the near future. 

## Testing and Database Dialect Support
### Testing Method
Presently very limited testing has been conducted and has primarily been through an implementation of a REST API with limited coverage of selected data models. Further expanding and automating testing is an area for future updates.
### Database Dialect Support
These data models have only been validated for a PostgreSQL database running a deployment of the ODM2.1 schema. 



