from django.contrib import admin
from goods import models
from celery_tasks.static_html.tasks import generate_static_list_search_html,generate_static_sku_detail_html
# Register your models here.

class GoodsAdmin(admin.ModelAdmin):
    # 商品SPU表的后端管理器
    list_display = ['id','name']


    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_list_search_html.delay()


    def delete_model(self, request, obj):
        # obj.delete()
        generate_static_list_search_html.delay()


class SKUAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        obj.save()

        generate_static_sku_detail_html.delay(obj.id)




admin.site.register(models.Goods,GoodsAdmin)
admin.site.register(models.SKU,SKUAdmin)
