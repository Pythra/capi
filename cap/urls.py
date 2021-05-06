from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='home'),
    path('announcement/', views.announcement_form, name='announcement_form'),
    path('profile/update/', views.profile_form, name='profile_edit'),
    path('<slug:slug>/', views.post_detail, name='post_detail'),
    path('post/create/', views.post_create, name='post_form'),
    path('post/<slug:slug>/update/', views.PostUpdate.as_view(), name='post_update'),
    path('post/<slug:slug>/delete/', views.PostDelete.as_view(), name='post_confirm_delete'),
    path('capital/trade/', views.trade, name='trade'),
    path('user/settings/', views.settings, name='settings'),
    path('capital/withdraw/', views.withdraw, name='withdraw'),
    path('capital/payment/', views.payment, name='payment'),
    path('user/wallets/', views.wallets, name='wallets'),
    path('user/my/wallets/', views.my_wallets, name='my_wallets'),
    path('cryptocurrency/buy/', views.buy, name='buy'),
    path('FAQ/help/', views.faq, name='faq'),
    path('legal/terms/', views.terms, name='terms'),
    path('package/details/', views.plan_detail, name='plan_detail'),
    ]
