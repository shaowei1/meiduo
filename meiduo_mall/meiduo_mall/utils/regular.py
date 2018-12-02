import re

phone_number = re.compile('^1[345789]\d{9}$')
s = 'accounts/python/sms/token/?text=whei&image_code_id=b6ce7f29-0c7a-4770-932e-2c5b012d2213'

res = phone_number.match(s)

print(res)
