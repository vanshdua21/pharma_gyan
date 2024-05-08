from django.urls import path, include
from pharma_gyan_proj.apps.pharma_gyan import views

urlpatterns = [
    path('editor/', views.editor),
    path('editor/dashboard/', views.dashboard)
]