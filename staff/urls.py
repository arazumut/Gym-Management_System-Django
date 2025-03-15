from django.urls import path
from . import views

app_name = 'staff'

urlpatterns = [
    path('', views.staff_home, name='home'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('profile/', views.staff_profile, name='profile'),
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/check-in/', views.attendance_check_in, name='attendance_check_in'),
    path('attendance/check-out/', views.attendance_check_out, name='attendance_check_out'),
    path('leaves/', views.leave_list, name='leave_list'),
    path('leaves/request/', views.leave_request, name='leave_request'),
    path('leaves/<int:pk>/', views.leave_detail, name='leave_detail'),
    path('shifts/', views.shift_list, name='shift_list'),
    path('shifts/<int:pk>/', views.shift_detail, name='shift_detail'),
    path('performance/', views.performance_list, name='performance_list'),
    path('performance/<int:pk>/', views.performance_detail, name='performance_detail'),
    path('payroll/', views.payroll_list, name='payroll_list'),
    path('payroll/<int:pk>/', views.payroll_detail, name='payroll_detail'),
] 