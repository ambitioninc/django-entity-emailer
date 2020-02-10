from django.dispatch import Signal


# An event that will be fired prior to an email being sent
pre_send = Signal(providing_args=['email', 'event', 'context', 'message'])

# An event that will be fired if an exception occurs when trying to send an email
email_exception = Signal(providing_args=['email', 'exception'])
