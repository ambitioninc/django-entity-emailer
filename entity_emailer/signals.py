from django.dispatch import Signal


# An event that will be fired prior to an email being sent
pre_send = Signal(providing_args=['email', 'event', 'context', 'message'])
