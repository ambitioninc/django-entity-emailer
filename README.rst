.. image:: https://travis-ci.org/ambitioninc/django-entity-emailer.svg?branch=develop
    :target: https://travis-ci.org/ambitioninc/django-entity-emailer

Django Entity Emailer
=====================

Do you:

- Use `Django-Entity`_?
- Want to send emails to entities easily?
- Want a record of emails sent?
- Want automatic assurance that you don't accidentally send hundreds
  of emails over the course of a few minutes?

Then use Django Entity Emailer!

.. _`Django-Entity`: https://github.com/ambitioninc/django-entity

Installation
------------

This package can currently be installed by downloading and installing
from source:

    git clone
    python setup.py install

Coming soon: ``pip install``.


Setup and Configuration
-----------------------

In order to use django-entity-emailer, you must be mirroring entities
using the `Django-Entity`_
framework. Additionally, in order to send email to entities, those
entities must include a value for the key ``'email'`` in their
``entity_meta`` field.

.. _`Django-Entity`: https://github.com/ambitioninc/django-entity

If both of those conditions are true, setup is fairly straightforward:

1. Add ``entity_emailer`` to ``INSTALLED_APPS``.

#. Either set a value for ``settings.ENTITY_EMAILER_FROM_EMAIL``, or be
   sure that the ``settings.DEFAULT_FROM_EMAIL`` is set to an
   appropriate value.

#. Ensure that all the dependencies are installed and listed in ``INSTALLED_APPS``

   - pip: ``django-db-mutex``, INSTALLED_APPS: ``db_mutex``

   - pip: ``django-entity-subscription``, INSTALLED_APPS: ``entity_subscription``

#. Add the scheduled email task to your ``CELERYBEAT_SCHEDULE`` (see
   configuring celery section).

#. Run ``python manage.py syncdb`` and ``python manage.py migrate``

#. Ensure that a email medium is set up by running ``python manage.py
   add_email_medium``.

When sending an email, django-entity-emailer will first check if the
``ENTITY_EMAILER_FROM_EMAIL`` exists. If it does, it will use that value
in the email's 'from' field, otherwise it will fall back to the value
set in ``DEFAULT_FROM_EMAIL``.

Finally, django-entity-emailer uses `django-entity-subscription`_ for
subscription management. This libary makes it easy for developers and
users to manage what sorts of notifications users recieve. However, it
does require some configuration. For a simple emailer configuration,
see the 'Basic entity-subscription configuration' section.

.. _`django-entity-subscription`: https://github.com/ambitioninc/django-entity-subscription


Getting ``'email'`` into ``'entity_meta'``
``````````````````````````````````````

The requirement that entities be mirrored with an ``'email'`` field in
their ``entity_meta`` is not difficult.

After installing django-entity, it is as simple as creating a model
inheriting from ``entity.BaseEntityModel``, with a ``get_entity_meta``
that returns the email along with any other data to be mirrored. A
simple example could be:

.. code:: Python

    from django.db import models
    from entity import BaseEntityModel

    class Account(BaseEntityModel)
        username = models.CharField(max_length=64)
        email = models.CharField(max_length=254)

        def get_entity_meta(self):
           return {'email': self.email, 'username': self.username}


Also note that it is not necessary for every mirrored entity to
include an email, only those entities that will actually be sent
emails need to have emails mirrored in their `entity_meta`s.

For a more complete description of how entity mirroring works, see the
documentation for django-entity.


Configuring Celery
``````````````````

To use the email scheduling feature of ``entity_emailer``, you must add
the appropriate task to your ``CELERYBEAT_SCHEDULE``. For a general
introduction to configuring periodic celery tasks in Django, see the
official guide, `Celery Periodic Tasks`.

.. _`Celery Periodic Tasks`: http://celery.readthedocs.org/en/latest/userguide/periodic-tasks.html

In short, it should be enough to add the following to your existing
celerybeat schedule.

.. code:: Python

    CELERYBEAT_SCHEDULE = {
        # ...
        'send_scheduled_emails': {
            'task': 'entity_emailer.tasks.SendUnsentScheduledEmails',
            'schedule': timedelta(minutes=1),
        },
        # ...
    }


Making sure to use a value for ``'schedule'`` that is appropriate for
the volume of emails, and server resources.


Basic entity-subscription configuration
```````````````````````````````````````

In order to ensure that users of your site will not recieve emails
that they don't want to recieve, the entity-emailer application ties
in to the `entity-subscription` framework. As a developer it is up to
you to expose the ability for users to subscribe and unsubscribe from
emails. Here, we will show the basic configuration required to start
sending emails.

.. _`entity-subscription`: https://github.com/ambitioninc/django-entity-subscription

Running ``manage.py add_email_medium`` will add the medium that
entity-emailer relies on to send emails. We must also have a source of
emails, and a subscription to that combination of email and source.

.. code:: Python

    from entity_emailer import get_medium
    from entity_subscription.models import Source, Subscription
    from entity import Entity
    from django.contrib.contenttypes.models import ContentType

    super_entity=Entity.objects.get_for_obj(my_group_object)
    user_entity_type = ContentTypes.objects.get_for_model(MyUserModel)

    email_medium = get_medium()
    admin_source = Source.objects.create(
        name='admin', display_name='Admin Notifications',
        description='Important notifications for the site Admin.',
    )
    Subscription.objects.create(
        source=admin_source, medium=email_medium,
        entity=super_entity, subentity_type=user_entity_type
    )


Send an Email Immediately
--------------------------------------------------

Sending an email immediately is as simple as saving a record to the
database. Django-entity-emailer listens to the post-save signal sent
for the Email model and spawns a celery task to send the email
asynchronously.

A prerequisite to sending an email is categorizing it into a
source. Categorizing emails into sources makes it easier to allow
users to unsubscribe from types of emails they don't wish to
receive. We have set up a source above, called ``admin_source``, for the
examples below, we will be using a source called ``marketing_source``.

Before we can send an email, we also need to create an ``EmailTemplate``
for the context of our email to fill in. An email template is simply a
reference to a django template to be filled in with some context.

This object can use a path that Django's template loaders will
understand, or store the template directly as a TextField. Here, we're
storing a simple text template. The different possibilities for
constructing an ``EmailTemplate`` object are discussed more deeply in
the "Email Templates" section.

.. code:: Python

    new_item_template = EmailTemplate.objects.create(
        template_name='simple item email',
        template_text='Check out {{ item }} for the price of {{ value }}!'
    )


Once an email type and template have been created, sending an email is
as simple as creating an email field without specifying a ``scheduled``
field.

.. code:: Python

    send_to_entity = Entity.objects.get_for_obj(some_user_with_an_email)

    Email.objects.create(
        source=marketing_source,
        send_to=send_to_entity,
        subject='This is a great offer!',
        template=new_item_template,
        context={'item': 'new car', 'value': '$35,000'}
    )

By saving this field, an email will be sent to the email stored in
``send_to_entity.entity_meta['email']``.

Email an individual
```````````````````

As seen in the example above, emailing an individual is as simple as
specifying the appropriate entity in the ``Email.send_to``
field. Additionally, because django-entity supports super-entity and
sub-entity relationships, it is very easy to send emails to groups of
individuals.


Email a group
`````````````

Emailing all the users in a group comes nearly for free if the group
is correctly mirrored in django-entity. Sending the email is still as
simple as saving an instance of ``Email``.

There are two changes we make from the example for sending to an
individual.

First, the ``sent_to`` field is still an entity, but instead of an
entity with an ``entity_meta['email']`` value, it should be an entity
that has a super-entity relationship to the entities the emails are to
be sent to.

Second, a ``subentity_type`` field specifies what type of subentity we
want to email All sub-entities of the ``send_to`` entity and of the type
specified by ``subentity_type`` must have an 'email' set in their
``entity_meta``.

A complete example is below:

.. code:: Python

    from entity_emailer.models import Email

    from entity.models import Entity
    from django.contrib.contenttypes import ContentType

    from my_example_app.models import Newsletter, NewsletterSubscribers

    # This send_to_entity has sub-entities we want to send to.
    marketing_news_today = Newsletter.objects.get(name='Marketing News Today')
    send_to_entity = Entity.objects.get_for_obj(marketing_news_today)

    Email.objects.create(
        source=marketing_source,
        # our send_to_entity, is a newsletter, a super-entity of
        # NewsletterSubscribers
        send_to=send_to_entity,
        # Below is our subentity type, NewsletterSubscribers
        subentity_type=ContentType.objects.get_for_model(NewsletterSubscribers)
        subject='This is a great offer!',
        template=new_item_template,
        context={'item': 'new car', 'value': '$35,000'}
    )

Once this email is saved to the database, the email will be sent to all
of the sub-entities of the ``marketing_news_today`` entity automatically.

This allows you to email any group of users that exists in your django
application without having to write custom ORM queries to pull that
group out of the database and organize their email addresses.


Send An Email at a Scheduled Time
---------------------------------

Sending an email at a scheduled time is just as easy as sending one
immediately. Assuming that the ``CELERYBEAT_SCHEDULE`` is correctly
configured, as described in the "Setup and Configuration" section, the
only difference from the process described above is that you must
provide a value for the ``scheduled`` field.

.. code:: Python

    from datetime import datetime

    Email.objects.create(
        source=marketing_source,
        send_to=send_to_entity,
        subentity_type=ContentType.objects.get_for_model(NewsletterSubscribers)
        subject='This is a great offer!',
        template=new_item_template,
        context={'item': 'New Hoverboard', 'value': '$35,000'}
        scheduled=datetime(year=2022, month=01, day=01, hour=12),
    )

The email created above will be sent at the time in the ``scheduled``
field, UTC.

Additionally, scheduled emails that are processed at the same time
will re-use a connection to the SMTP server to minimize overhead.


Unsubscribing
-------------

Users may want to be able to unsubscribe from certain types of
emails. This is easy in django-entity-emailer. Emails can be
unsubscribed from by individual sources, by using the
entity-subscription framework.

.. code:: Python

    from entity_emailer import get_medium
    from entity_subscription import Source, Unsubscribe

    admin_emails = Source.objects.get(name='admin')
    Unsubscribe.objects.create(
        entity=entity_of_user_to_unsub,
        source=admin_emails
        medium=get_medium()
    )

This user will be excluded both from receiving emails of this type
that were sent to them individually, or as part of a group email.


Email Templates
---------------

Instance of ``EmailTemplate`` are used to store email templates that can
be re-used with different contexts.

The possible fields on ``EmailTemplate`` are:

- ``template_name`` - Required. A descriptive name for the template.
- ``text_template_path`` - A path to a template for a text email.
- ``html_template_path`` - A path to a template for an html email.
- ``text_template`` - A TextField for inputing a text email template directly.
- ``html_template`` - A TextField for inputing an html email template directly.

Both a text and html template may be provided, either through a path
to the template, or a raw template object. However, for either text or
html templates, both a path and raw template should not be provided.

If all of ``text_template_path``, ``text_template``, ``html_template_path``,
and ``html_template`` are missing, if ``text_template_path`` and
``text_template`` are both provided, or if ``html_template_path`` and
``html_template`` are both provided, a ``ValidationError`` will be raised.

The email sending task will take care of rendering the template,
and creating a text or text/html message based on the rendered
template.
