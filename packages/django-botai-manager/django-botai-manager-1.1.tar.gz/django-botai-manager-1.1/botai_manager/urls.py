# Django
from django.urls import path
# Views
from .views import company_info


urlpatterns = [
    path('manager/company/<int:company_id>', company_info),
]
