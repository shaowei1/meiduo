from meiduo_mall.libs.yuntongxun.sms import CCP
from celery_tasks.main import app


# 发送短信任务
@app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    ccp = CCP()
    ccp.send_template_sms(mobile, [sms_code, '5'], 1)


@app.task(name='a_print')
def a_print():
    print('aaaa')
