[![Test](https://github.com/acdh-oeaw/django-story-map/actions/workflows/test.yml/badge.svg)](https://github.com/acdh-oeaw/django-story-map/actions/workflows/test.yml)
[![flake8 Lint](https://github.com/acdh-oeaw/django-story-map/actions/workflows/lint.yml/badge.svg)](https://github.com/acdh-oeaw/django-story-map/actions/workflows/lint.yml)
[![codecov](https://codecov.io/gh/acdh-oeaw/django-story-map/branch/master/graph/badge.svg?token=EK3LO3URJK)](https://codecov.io/gh/acdh-oeaw/django-story-map)
[![pypi](https://github.com/acdh-oeaw/django-story-map/actions/workflows/pypi.yml/badge.svg)](https://github.com/acdh-oeaw/django-story-map/actions/workflows/pypi.yml)
[![PyPI version](https://badge.fury.io/py/django-story-map.svg)](https://badge.fury.io/py/django-story-map)
# Django Story Map

A django app to create/edit/publish story maps using https://storymap.knightlab.com/

## install

* `pip install django-story-map`
* add `story_map` to `INSTALLED_APPS` in your settings-file( see e.g. the example project `./djangobaseproject/settings.py`)
* add the story_maps urls to your project's urls (see e.g. the example project `./djangobaseproject/urls.py`)


## features

* create story maps via django-admin interface
* donwload/copy story-maps created via knightlab's interface
* show storymaps
* provide storymaps data via JSON-API-Endpoint

This project was bootstraped by [djangobase-cookiecutter](https://github.com/acdh-oeaw/djangobase-cookiecutter)