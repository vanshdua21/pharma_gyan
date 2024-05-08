"""
This module represents the Helth-Check controller end-point.

This end-point is not part of the specification and is configured
directly with Flask

Example:
    To open the end-point 'http://<host>:<port>/health'
"""
import json
import subprocess
from django.shortcuts import render
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import logging


@csrf_exempt
def home(request):
    if (request.method == 'GET'):
        logging.debug('GET Request')
    if (request.method == 'POST'):
        logging.debug('POST Request')
    return render(request, "index.html")


@csrf_exempt
def health(request):
    """
    Get the health of the service.

    Returns:
        Ok response
    """

    logging.debug(f"Entered health check DEBUG level Logs")
    logging.info(f"Entered health check INFO level Logs")
    logging.debug('This is the first log')
    logging.debug('second log')
    logging.debug({'seconnd': 'log', 'account_number': 'ML12345', 'mobiles': ['8839524749', '9988776699']})
    logging.debug(['this is my no. 8839524749'])
    return HttpResponse(json.dumps({'success': True}))


@csrf_exempt
def setup_django_admin(request):
    from django.core.management import call_command
    from django.contrib.auth.models import User
    body = {}
    try:
        body = json.loads(request.body.decode('utf-8'))
    except Exception as ex:
        logging.debug(f"Unable to Json Load request body, validate_settlement_offer, exception : {ex}")
    username = body.get("username", None)
    password = body.get("password", None)
    email = body.get("email", None)
    try:
        call_command('migrate', verbosity=3, interactive=False)
        u = User(username=username)
        u.set_password(password)
        u.is_superuser = True
        u.is_staff = True
        u.save()
    except Exception as ex:
        return HttpResponse(json.dumps({"success": False, "error": str(ex)}))


    return HttpResponse(json.dumps({'success': True}))
