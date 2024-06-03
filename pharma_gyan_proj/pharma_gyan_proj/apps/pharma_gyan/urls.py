from django.urls import path, include
from pharma_gyan_proj.apps.pharma_gyan import views

urlpatterns = [
    path('editor/', views.editor),
    path('editor/dashboard/', views.dashboard),
    path('editor/promoCode', views.promo_code),
    path('editor/viewPromoCode', views.view_promo_code),
    path("editor/upsertPromoCode/", views.upsert_promo_code),
    path("editor/summernote/", views.summernote),
    path("editor/saveSummernote/", views.save_summernote),
    path("editor/addUser/", views.addUser),
    path("editor/editUser/", views.editUser),
    path("editor/viewUsers/", views.viewUsers),
    path("editor/upsertUser/", views.upsertUser),
    path("editor/deleteUser/<str:userId>/", views.deleteUser),
]