from django.test import TestCase

# Create your tests here.

import re

s = '/accounts/python/sms/token/'

get = re.match(r'/accounts/([\d\w]+)/sms/token/$', s)

print(get.group(0))
print(get.group(1))
