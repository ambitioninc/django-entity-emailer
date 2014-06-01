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

Coming soon: `pip install`.


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
2. Either set a value for `settings.ENTITY_EMAILER_FROM_EMAIL`, or be
   sure that the `settings.DEFAULT_FROM_EMAIL` is set to an
   appropriate value. 
4. Be sure that `django.contrib.contenttypes` is in `INSTALLED_APPS`.
5. Run `python manage.py syncdb`

When sending an email, django-entity-emailer will first check if the
`ENTITY_EMAILER_FROM_EMAIL` exists. If it does, it will use that value
in the email's 'from' field, otherwise it will fall back to the value
set in `DEFAULT_FROM_EMAIL`.

### Getting `'email'` into `'entity_meta'`

The requirement that entities be mirrored with an `'email'` field in
their `entity_meta` is not difficult.

After installing django-entity, it is as simple as creating a model
inheriting from `entity.BaseEntityModel`, with a `get_entity_meta`
that returns the email along with any other data to be mirrored. A
simple example could be:

```python
from django.db import models
from entity import BaseEntityModel

class Account(BaseEntityModel)
    username = models.CharField(max_length=64)
    email = models.CharField(max_length=254)

    def get_entity_meta(self):
        return {'email': self.email, 'username': self.username}
```

Also note that it is not necessary for every mirrored entity to
include an email, only those entities that will actually be sent
emails need to have emails mirrored in their `entity_meta`s.

For a more complete description of how entity mirroring works, see the
documentation for django-entity.

Send an Email Immediately
--------------------------------------------------

Sending an email immediately is as simple as saving a record to the
database. Django-entity-emailer listens to the post-save signal sent
for the Email model and spawns a celery task to send the email
asynchronously.

A prerequisite to sending an email is categorizing it into an
email-type. Categorizing emails into types makes it easier to allow
users to unsubscribe from types of emails they don't wish to receive.

``` python
from entity.models import Entity
from entity_emailer.models import Email, EmailTemplate, EmailType

marketing_email_type, created = EmailType.objects.get_or_create(
    name='marketing',
    description='Emails with new and exciting offers!'
)
```

Before we can send an email, we also need to create an `EmailTemplate`
for the context of our email to fill in. An email template is simply a
reference to a django template to be filled in with some context.

This object can use a path that Django's template loaders will
understand, or store the template directly as a TextField. Here, we're
storing a simple text template. The different possibilities for
constructing an `EmailTemplate` object are discussed more deeply in
the "Email Templates" section.

```python
new_item_template = EmailTemplate.objects.create(
    template_name='simple item email',
    template_text='Check out {{ item }} for the price of {{ value }}!'
)
```

Once an email type and template have been created, sending an email is
as simple as creating an email field without specifying a `scheduled`
field.

```python
send_to_entity = Entity.objects.get_for_obj(some_user_with_an_email)

Email.objects.create(
    email_type=marketing_email_type,
    send_to=send_to_entity,
    subject='This is a great offer!',
    template=new_item_template,
    context={'item': 'new car', 'value': '$35,000'}
)
```

By saving this field, an email will be sent to the email stored in
`send_to_entity.entity_meta['email']`.

### Email an individual

As seen in the example above, emailing an individual is as simple as
specifying the appropriate entity in the `Email.send_to`
field. Additionally, because django-entity supports super-entity and
sub-entity relationships, it is very easy to send emails to groups of
individuals.

### Email a group

Emailing all the users in a group comes nearly for free if the group
is correctly mirrored in django-entity. Sending the email is still as
simple as saving an instance of `Email`.

There are two changes we make from the example for sending to an
individual.

First, the `sent_to` field is still an entity, but instead of an
entity with an `entity_meta['email']` value, it should be an entity
that has a super-entity relationship to the entities the emails are to
be sent to.

Second, a `subentity_type` field specifies what type of subentity we
want to email All sub-entities of the `send_to` entity and of the type
specified by `subentity_type` must have an 'email' set in their
`entity_meta`.

A complete example is below:

```python
from entity_emailer.models import Email

from entity.models import Entity
from django.contrib.contenttypes import ContentType

from my_example_app.models import Newsletter, NewsletterSubscribers

# This send_to_entity has sub-entities we want to send to.
marketing_news_today = Newsletter.objects.get(name='Marketing News Today')
send_to_entity = Entity.objects.get_for_obj(marketing_news_today)

Email.objects.create(
    email_type=marketing_email_type,
    # our send_to_entity, is a newsletter, a super-entity of
    # NewsletterSubscribers
    send_to=send_to_entity,
    # Below is our subentity type, NewsletterSubscribers
    subentity_type=ContentType.objects.get_for_model(NewsletterSubscribers)
    subject='This is a great offer!',
    template=new_item_template,
    context={'item': 'new car', 'value': '$35,000'}
)
```

Once this email is saved to the database, the email will be sent to all
of the sub-entities of the `marketing_news_today` entity automatically.

This allows you to email any group of users that exists in your django
application without having to write custom ORM queries to pull that
group out of the database and organize their email addresses.


Unsubscribing
--------------------------------------------------

Users may want to be able to unsubscribe from certain types of
emails. This is easy in django-entity-emailer. Emails can be
unsubscribed from by individual `EmailType`.

```python
from entity_emailer import EmailType, Unsubscribed

admin_emails = EmailType.objects.get(name='admin')
Unsubscribed.objects.create(
    entity=entity_of_user_to_unsub,
    email_type=admin_emails
)
```

This user will be excluded both from receiving emails of this type
that were sent to them individually, or as part of a group email.


Email Templates
--------------------------------------------------

Instance of `EmailTemplate` are used to store email templates that can
be re-used with different contexts.

The possible fields on `EmailTemplate` are:

- `template_name` - Required. A descriptive name for the template.
- `text_template_path` - A path to a template for a text email.
- `html_template_path` - A path to a template for an html email.
- `text_template` - A TextField for inputing a text email template directly.
- `html_template` - A TextField for inputing an html email template directly.

Both a text and html template may be provided, either through a path
to the template, or a raw template object. However, for either text or
html templates, both a path and raw template should not be provided.

If all of `text_template_path`, `text_template`, `html_template_path`,
and `html_template` are missing, if `text_template_path` and
`text_template` are both provided, or if `html_template_path` and
`html_template` are both provided, a `ValidationError` will be raised.

The email sending task will take care of rendering the template,
and creating a text or text/html message based on the rendered
template.
