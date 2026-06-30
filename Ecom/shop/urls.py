from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='products'),
    path('orders/', views.order_list, name='orders'),

    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('increase/<int:item_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease/<int:item_id>/', views.decrease_quantity, name='decrease_quantity'),

    path('session-cart/', views.session_cart, name='session_cart'),
    path('add-session/<int:product_id>/', views.add_to_session_cart, name='add_to_session_cart'),
    path('remove-session/<int:product_id>/', views.remove_session_item, name='remove_session_item'),

   # order crud
   path('order-update/<int:order_id>/', views.update_order_status, name='update_order'),
   path('order-delete/<int:order_id>/', views.delete_order, name='delete_order'),

   # profile
   path('profile/', views.profile, name='profile'),
   path('profile/update/', views.update_profile, name='update_profile'),
   path('checkout/', views.checkout, name='checkout'),
]   