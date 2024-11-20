from . import views
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.signin,name='signin'),
    path('adminDashboard', views.adminDashboard,name='adminDashboard'),
    path('userDashboard', views.userDashboard,name='userDashboard'),
    path('delete/<int:id>', views.delete,name='delete'),
    path('ajax/generate_id/', views.generate_id, name='ajax_generate_id'),
    path('ajax/get_otp/', views.get_otp, name='ajax_get_otp'),
]