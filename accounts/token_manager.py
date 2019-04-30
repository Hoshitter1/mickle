from __future__ import absolute_import, unicode_literals
import uuid
from uuid import uuid4
from django.utils.encoding import force_bytes, force_text
import datetime

def create_key():

    key = uuid.uuid4().hex
    return key

def create_expiration_date():
    now = datetime.datetime.now()

    expiration_date = now + datetime.timedelta(hours=1)

    return expiration_date
