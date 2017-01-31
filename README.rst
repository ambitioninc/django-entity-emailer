.. image:: https://travis-ci.org/ambitioninc/django-entity-emailer.svg?branch=develop
    :target: https://travis-ci.org/ambitioninc/django-entity-emailer

Django Entity Emailer
=====================

Do you:

- Use `Django-Entity-Event`_?
- Want to have emailing as another medium for entity events?
- Want a record of emails sent?
- Want automatic assurance that you don't accidentally send hundreds
  of emails over the course of a few minutes?

Then use Django Entity Emailer!

.. _`Django-Entity-Event`: https://github.com/ambitioninc/django-entity-event

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
using the `django-entity`_
framework.
Additionally, in order to send email to entities, those
entities must include a value for the key ``'email'`` in their
``entity_meta`` field.

.. _`django-entity`: https://github.com/ambitioninc/django-entity

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

Finally, django-entity-emailer is an installable medium that is used with
`django-entity-event`_ . This libary makes it easy for developers and
users to manage what sorts of notifications users recieve over various
mediums. However, it does require some configuration. For a simple emailer configuration,
see the 'Basic entity-subscription configuration' section.

.. _`django-entity-event`: https://github.com/ambitioninc/django-entity-event


Getting ``'email'`` into ``'entity_meta'``
``````````````````````````````````````````

The requirement that entities be mirrored with an ``'email'`` field in
their ``entity_meta`` is not difficult.

After installing django-entity, it is as simple as creating a model
inheriting from ``entity.BaseEntityModel``, with a ``get_entity_meta``
that returns the email along with any other data to be mirrored. A
simple example could be:

.. code:: python

    from django.db import models
    from entity import BaseEntityModel

    class Account(BaseEntityModel)
        username = models.CharField(max_length=64)
        email = models.CharField(max_length=254)

        def get_entity_meta(self):
            return {'email': self.email, 'username': self.username}


Also note that it is not necessary for every mirrored entity to
include an email, only those entities that will actually be sent
emails need to have emails mirrored in their ``entity_meta``.

For a more complete description of how entity mirroring works, see the
documentation for django-entity.


Basic entity-event configuration
```````````````````````````````````````

In order to ensure that users of your site will not recieve emails
that they don't want to recieve, the entity-emailer application ties
in to the `entity-event` framework. As a developer it is up to
you to expose the ability for users to subscribe and unsubscribe from
emails. Here, we will show the basic configuration required to start
sending emails.

.. _`entity-event`: https://github.com/ambitioninc/django-entity-event

Running ``manage.py add_email_medium`` will add the medium that
entity-emailer relies on to send emails. We must also have a source of
emails, and a subscription to that combination of email and source.

.. code:: python

    from entity_emailer import get_medium
    from entity_event.models import Source, Subscription
    from entity.models import Entity, EntityKind

    super_entity = Entity.objects.get_for_obj(my_group_object)
    user_entity_kind = EntityKind.objects.get(name='myusermodel')

    email_medium = get_medium()
    admin_source = Source.objects.create(
        name='admin', display_name='Admin Notifications',
        description='Important notifications for the site Admin.',
    )
    Subscription.objects.create(
        source=admin_source, medium=email_medium,
        entity=super_entity, subentity_kind=user_entity_kind
    )


Along with this, you will need to associate the email medium with a
``RenderingStyle`` object in entity event so that it can perform email
rendering. More about this in the next section.

Django Entity Emailer must know the email addresses of entities and assumes that an
email address has been mirrored by default in the entity metadata. By default, it
uses the "email" metadata key, but this can be overridden by setting a
``ENTITY_EMAILER_EMAIL_KEY`` in the settings.

Django Entity Emailer also has the ability to exclude certain entities from ever
being emailed. In order to do this, mirror metadata that when ``None`` or ``False``
means that the entity should never be emailed. Then set the ``ENTITY_EMAILER_EXCLUDE_KEY``
setting to the key of this metadata.

Sending an Email about an Event
-------------------------------

Sending an email is as simple as saving an event to the database
and subscribing to the email medium after templates are defined for the
email. The entity emailer will go through
the events, send out emails to the subscribed targets, and mark the
events as seen so that duplicate emails are never sent.

For example, let's say that we wish to be notified via email when a user
logs into a site. Assuming that the email medium and admin sources are setup
from our previous examples, we can make an email template (login.html) that looks like the
following:

.. code:: python

    {{ user }} just logged in!

We then set up a rendering style and a context renderer for this template so that
emails can be rendered:

.. code:: python

    from entity_event.models import RenderingStyle, ContextRenderer

    style = RenderingStyle.objects.create(name='email')
    ContextRenderer.objects.create(
        rendering_style=style,
        source=admin_source,
        html_template_path='templates/login.html',
    )

When the context renderer is in place, the email medium will need to be updated to point
to the appropriate rendering style we want to use. To continue our example:

.. code:: python

    email_medium.rendering_style = style
    email_medium.save()

Once we have the rendering style in place, assume an Event is created with the following context:

.. code:: python

    {
        'user': 'User name'
    }
    
When this happens, an email will be sent to the subscribed user that says 'User name just logged in!'.

The subject line of this email will use the first 40 characters from the rendered email template. However,
if one specifies a <title> HTML tag in their template, the contents of the tag will be used as the
email subject.

For more detailed information on event rendering, checkout `django-entity-event`_.

.. _`django-entity-event`: https://github.com/ambitioninc/django-entity-event


Unsubscribing
-------------

Users may want to be able to unsubscribe from certain types of
emails. This is easy in django-entity-emailer. Emails can be
unsubscribed from by individual sources, by using the
entity-subscription framework.

.. code:: python

    from entity_emailer import get_medium
    from entity_event import Source, Unsubscribe

    admin_emails = Source.objects.get(name='admin')
    Unsubscribe.objects.create(
        entity=entity_of_user_to_unsub,
        source=admin_emails
        medium=get_medium()
    )

This user will be excluded both from receiving emails of this type
that were sent to them individually, or as part of a group email.


Showing Emails in the Browser
-----------------------------

Users may view emails in a browser with this application. This is accomplished by including
the ``entity_emailer`` urls into the Django project and providing the ``view_uid`` of the email as the url argument.
The url view will use the text/html templates of the email to render it as a web page.


Release Notes
-------------

* 0.9.0

    * Added Django 1.8 support and dropped 1.6 support

* 0.8.4

    * Added the abilty to override the email key in entity metadata.
    * Added the ability to exlude entities from being emailed based on a metadata key.

* 0.8.1

    * Added Django 1.7 support
    * Added Python 3.4 support

* 0.7.1

    * Squashed entity emailer migrations and removed entity subscription dependency.

* 0.7

    * Converted entity emailer to solely be a medium for entity event.

* 0.6

    * Added a ``recipients`` field to the ``Email`` model and removed the ``send_to`` field. This allows the user
        to provide more than one receiver (or group of receivers) for the email.

* 0.5

    * Added a ``context_loader`` field on the ``EmailTemplate`` model. This function allows a user to provide a function
        path that for fetching and returning data from the stored ``Email`` context.
    * Added a basic ``EmailView`` and urls for rendering emails through a Django view.

* 0.4

    * Updated to use ``EntityKind`` models rather than ``ContentType`` models for specifying entity groups.
        A schema migration to remove the old ``subentity_type`` field while adding the new ``subentity_kind``
        field were added so that users may make appropriate data migrations. Note that it is up to the
        user to write the appropriate data migration for converting entity types to entity kinds.
