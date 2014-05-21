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
4. Be sure that `django.contrib.contenttypes` is in `INSTALLED_APPS`.
5. Run `python manage.py syncdb`


Send an Email Immediately
--------------------------------------------------

Sending an email immediately is as simple as saving a record to the
database. Django-entity-emailer listens to the post-save signal sent
for the Email model and spawns a celery task to send the email
asynchronously.

A prerequisite to sending an email is categorizing it into an
email-type. Categorizing emails into types makes it easier to allow
users to unsubscribe from types of emails they don't wish to recieve.

``` python
from entity.models import Entity
from entity_emailer.models import Email, EmailType

marketing_email_type, created = EmailType.objects.get_or_create(
    name='marketing',
    description='Emails with new and exciting offers!'
)
```

Once an email type has been created, sending an email is as simple as
creating an email field without specifying a `scheduled` field.

```python
send_to_entity = Entity.objects.get_for_obj(some_user_with_an_email)

Email.objects.create(
    email_type=marketing_email_type,
    send_to=send_to_entity,
    subject='This is a great offer!',
    html_template_path='/path/to/templates/html/marketing1.html',
    text_template_path='/path/to/templates/text/marketing1.txt',
    context={'item': 'new car', 'value': '$35,000'}
)
```

By saving this field, an email will be sent to the email stored in
`send_to_entity.entity_meta['email']`.
