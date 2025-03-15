from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('widgets/', views.widget_list, name='widget_list'),
    path('widgets/<int:pk>/', views.widget_detail, name='widget_detail'),
    path('widgets/add/', views.widget_add, name='widget_add'),
    path('widgets/<int:pk>/edit/', views.widget_edit, name='widget_edit'),
    path('widgets/<int:pk>/remove/', views.widget_remove, name='widget_remove'),
    path('announcements/', views.announcement_list, name='announcement_list'),
    path('announcements/<int:pk>/', views.announcement_detail, name='announcement_detail'),
    path('announcements/add/', views.announcement_add, name='announcement_add'),
    path('announcements/<int:pk>/edit/', views.announcement_edit, name='announcement_edit'),
    path('reports/', views.report_list, name='report_list'),
    path('reports/<int:pk>/', views.report_detail, name='report_detail'),
    path('reports/generate/', views.report_generate, name='report_generate'),
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/<int:pk>/', views.task_detail, name='task_detail'),
    path('tasks/add/', views.task_add, name='task_add'),
    path('tasks/<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),
] 