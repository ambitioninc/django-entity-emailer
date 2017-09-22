from django_dynamic_fixture import G, F
import uuid

from entity_emailer.models import Email


def g_email(**kwargs):
    view_uid = kwargs.pop('view_uid', uuid.uuid4())
    context = kwargs.pop('context', None)
    if context is not None:
        return G(Email, view_uid=view_uid, event=F(context=context), **kwargs)
    else:
        return G(Email, view_uid=view_uid, **kwargs)
