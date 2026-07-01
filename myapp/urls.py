from django.contrib import admin
from django.urls import path
from myapp import views
from myapp.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/',views.signupfunction),
    path('signup_post/',views.signupfunction_post),
    path('login/',views.loginfunction),
    path('login_post/',views.login_post),
    path('logout/', views.logout_view),
    path('viewprofile/',views.viewprofile),
    path('editprofile/', views.editprofile),
    path('editprofile_post/', views.editprofile_post),
    path('', views.home),
    path('uploaddocument/',views.uploaddocument),
    path('uploaddocument_post/',views.uploaddocument_post),
    path('viewdocument/',views.viewdocument),
    path('editdocument/<id>',views.editdocument),
    path('editdocument_post/',views.editdocument_post),
    path('deletedocument/<id>',views.deletedocument),
    path('change/',views.change_password),
    path('change_post/',views.change_password_post),
    path('forgot_password/', views.forgot_password),
    path('forgot_password_post/', views.forgot_password_post),
    path('reset_password/', views.reset_password),
    path('reset_password_post/', views.reset_password_post),
]

