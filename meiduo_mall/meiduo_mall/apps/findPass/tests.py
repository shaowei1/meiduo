from django.test import TestCase

# Create your tests here.

import re

s = '/image_codes/39fbf3a3-1d83-47ab-8faa-2bcaadc7ef1f/'

get = re.match(r'/image_codes/([\d\w-]+)/$', s)

print(get.group(0))
print(get.group(1))
