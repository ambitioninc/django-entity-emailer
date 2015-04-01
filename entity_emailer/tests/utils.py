from django_dynamic_fixture import N, G, F
from uuidfield.fields import UUIDField

from entity_emailer.models import Email


def n_email(**kwargs):
    view_uid = kwargs.pop('view_uid', UUIDField()._create_uuid())
    return N(Email, view_uid=view_uid, persist_dependencies=False, **kwargs)


def g_email(**kwargs):
    view_uid = kwargs.pop('view_uid', UUIDField()._create_uuid())
    context = kwargs.pop('context')
    return G(Email, view_uid=view_uid, event=F(context=context), **kwargs)
