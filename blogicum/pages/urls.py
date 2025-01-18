from django.urls import path
from . import views


app_name = 'pages'

urlpatterns = [
    path('about/', view=views.About.as_view(), name='about'),
    path('rules/', view=views.Rules.as_view(), name='rules'),
]
