Release Notes
=============

v1.1.0
------
* Python 3.7
* Django 2.1
* Django 2.2

v1.0.0
------
* Django 2.0 support
* Add tox to support more versions

0.14.2
------
* Removed celery dependencies and autodiscover from settings file

0.14.1
------
* Added ability to set custom From Address

0.14.0
------
* Add Python 3.6 support
* Remove Django 1.8 support
* Add Django 1.9 support
* Add Django 1.10 support

0.13.2
------
* Fix issue where  entities with ENTITY_EMAILER_EXCLUDE_KEY=False were being emailed

0.13.1
------
* Python 3 ready

0.13.0
------
* Remove celery tasks and move methods onto interface. Application is now responsible for creating tasks to use for celery

0.12.0
------
* Check entity email address to ensure it exists and is not an empty string
