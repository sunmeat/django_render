from datetime import datetime
from django.urls import path, include
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from app import forms, views

# Автоматичний редирект на потрібну сторінку при запуску
def redirect_to_default_artist(request):
    return redirect('/artists/78/?tab=tracks')


urlpatterns = [
    # Головна сторінка тепер редиректить на конкретного артиста
    path('', redirect_to_default_artist, name='home'),

    path('login/',
         LoginView.as_view(
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context={
                 'title': 'Log in',
                 'year': datetime.now().year,
             }
         ),
         name='login'),

    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('admin/', admin.site.urls),

    # API
    path('api/v1/', include('api.urls')),

    # Ваші app URLs
    path('', include('app.urls')),   # залишаємо для всіх інших шляхів
]