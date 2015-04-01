from django_dynamic_fixture import G, F
from uuidfield.fields import UUIDField

from entity_emailer.models import Email


def g_email(**kwargs):
    view_uid = kwargs.pop('view_uid', UUIDField()._create_uuid())
    context = kwargs.pop('context', None)
    if context is not None:
        return G(Email, view_uid=view_uid, event=F(context=context), **kwargs)
    else:
        return G(Email, view_uid=view_uid, **kwargs)
