# AI VIEW - DJANGO BLOG API PLUGIN POC

This a small example plugin for AI VIEW, showing how and what you need to create a pluggable package


## Plugin Structure

1. you will need to create the package main folder with the same name as the main module folder name, for example here we created "**django_blog_api**" as the main package folder and inside it the main module folder "**django_blog_api**", this structure will help in building the package later to export the code with the package.
2. inside the main module you can create as many as apps inside it following the default Django APPS structure.
3. then you need to configer **pyproject.toml**, **setup.py** files and add the needed files for python package like setup.cfg if needed and LICENSE, MANIFEST.in, README.md, CHANGELOG.rst, CONTRIBUTING.rst, AUTHORS.rst
4. **IMPORTANT** make sure to add all the apps names you created to the main module **__init__.py** file in **__all__** variable, this step needed to make the package a plugable to AI VIEW.
5. inside the main package you need to create a **config** folder to define the general plugin settings like URLS.

## Plugin package bullied

to build a package, in the main package folder path, **NOT** the main module folder run 

    $  python -m pip install --upgrade build # run this in your system for the first time
    $  python -m build # run this inside the main package folder path to build it 

this will generate 2 folder **dist** and **name-of-package.egg-info** folders that will be used by pypi, 
1. each time you build **delete** both folder 
2. and **update the plugin version** in **pyproject.toml**

## Plugin package upload to pypi

to upload package to pypi, in the main package folder path, **NOT** the main module folder run 
    
    $ python -m pip install --upgrade twine # run this in your system for the first time
    $ python -m twine upload  dist/*  # run this inside the main package folder path to upload it 

## Plugin package installation from pypi

after you upload the package do a pip install

    $ pip install django-blog-api


### useful links

1. https://packaging.python.org/en/latest/tutorials/packaging-projects/
2. https://github.com/jazzband/django-redis
