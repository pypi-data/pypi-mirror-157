# Django
from django.urls import path
# Views
from apps.manager.views import apis
from apps.manager.models.company import *


urlpatterns = [
    path('company/<int:company_id>', apis.company_info),
]
