Release Notes
=============

v2.1.0
------
* More durable handling and retry logic for failures in bulk send unsent emails process

v2.0.4
------
* Bugfix for updated interface

v2.0.2
------
* Fix unique constraint when bulk creating emails

v2.0.1
------
* Fix for handling single failures in a batch of outgoing emails

v2.0.0.2
------
* Atomic decorator on event fetching

v2.0.0.1
------
* Fix unique constraint when bulk creating emails

v2.0.0
------
* Added bulk interface for converting to emails
* Add support for django 3.0, 3.1

v1.1.2
------
* Handle email render exceptions
* Add `exception` field
* Add `email_exception` signal

v1.1.1
------
* Add `pre_send` signal

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
