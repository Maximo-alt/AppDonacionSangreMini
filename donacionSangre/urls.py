from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('campanas/', views.campanas, name='campanas'),
    path('campanas/crear/', views.campana_crear, name='campana_crear'),
    path('campanas/<int:pk>/', views.campana_detalle, name='campana_detalle'),
    path('campanas/<int:pk>/editar/', views.campana_editar, name='campana_editar'),
    path('campanas/<int:pk>/eliminar/', views.campana_eliminar, name='campana_eliminar'),
    path('campanas/<int:pk>/inscribirse/', views.inscribirse_campana, name='inscribirse_campana'),
    path('campanas/<int:pk>/desinscribirse/', views.desinscribirse_campana, name='desinscribirse_campana'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]