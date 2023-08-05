#models
from apps.manager.models.company import Company

# rest framework
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
# from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError, transaction
from rest_framework.permissions import IsAuthenticated
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from oauth2_provider.decorators import protected_resource
from django.contrib.contenttypes.models import ContentType


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def company_info(request, company_id):
    """Return info company model

    Args:
        company_id (int): identifier company in db

    Returns(json):
        status(str): ok or error
        company(json): info company
    """

    # ct = ContentType.objects.get(model='company', app_label='models')
    # ct_class = ct.model_class()
    # company = ct_class.objects.filter(id=company_id).values()
    company, = Company.objects.filter(id=company_id).values()
    return Response({'status': 'ok', 'company': company}, status=status.HTTP_200_OK)

