from django.urls import path
from . import views

urlpatterns = [
    path('<int:build_id>/', views.builder_dashboard, name='builder_dashboard'),
    path('<int:build_id>/choose/<str:category>/', views.select_part, name='select_part'),
    path('<int:build_id>/install/<int:component_id>/', views.install_part, name='install_part'),
    path('remove/<int:item_id>/', views.remove_part, name='remove_part'),
    path('start/', views.initiate_build, name='initiate_build'),
    path('<int:build_id>/add-to-cart/', views.add_build_to_cart, name='add_build_to_cart'), 
    path('new-rig/', views.create_new_rig, name='create_new_rig'),   
    path('<int:build_id>/rename/', views.rename_build, name='rename_build'), 
]