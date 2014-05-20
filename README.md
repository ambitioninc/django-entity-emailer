[![Build Status](https://travis-ci.org/ambitioninc/django-entity-emailer.svg?branch=develop)](https://travis-ci.org/ambitioninc/django-entity-emailer)

Django Entity Emailer
==================================================

Do you:

- Use [Django-Entity](https://github.com/ambitioninc/django-entity)?
- Want to send emails to entities easily?
- Want a record of emails sent?
- Want automatic assurance that you don't accidentally send hundreds
  of emails over the course of a few minutes?

Then use Django Entity Emailer!


Installation
--------------------------------------------------

This package can currently be installed by downloading and installing
from source:

    git clone
    python setup.py install

Comming soon: `pip install`.


Setup and Configuration
--------------------------------------------------

In order to use django-entity-emailer, you must be mirroring entities
using the
[Django-Entity](https://github.com/ambitioninc/django-entity)
framework. Additionally, in order to send email to entities, those
entities must include a value for the key `'email'` in their
`entity_meta` field.

If both of those conditions are true, setup is fairly straightforward:

1. Add `entity_emailer` to `INSTALLED_APPS`.
2. Be sure that the `settings.DEFAULT_FROM_EMAIL` is set to an
   appropriate value. This is what will be sent in the 'from' field of
   emails.
3. Run `python manage.py syncdb`
