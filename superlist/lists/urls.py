from django.conf.urls import url

from .views import home_page, view_list, new_list, add_item

urlpatterns = [
    url(r'^(\d+)/$', view_list,name='view_list'),
    url(r'^(\d+)/add_item$', add_item, name='add_item'),
    url(r'^new$', new_list,name='new_list'),
]
