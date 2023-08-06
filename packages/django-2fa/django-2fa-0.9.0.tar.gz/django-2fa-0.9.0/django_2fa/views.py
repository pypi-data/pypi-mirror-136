import time

from django import http
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

import pyotp

from django_2fa.decorators import mfa_login_required
from django_2fa.forms import MFAForm, AddDeviceForm
from django_2fa.models import Device, MFARequest
import django_2fa.settings as mfa_settings


@mfa_login_required
def test_2fa(request):
  reset = request.GET.get('reset')
  if reset:
    del request.session['2fa_verfied']
    return http.HttpResponseRedirect(f'./?ts={time.time()}')

  return http.HttpResponse('2FA Successful', content_type="text/plain")


@login_required
def login_2fa(request):
  devices = Device.objects.filter(owner=request.user, setup_complete=True).order_by('name')
  goto = request.GET.get(mfa_settings.MFA_REDIRECT_FIELD, settings.LOGIN_REDIRECT_URL)

  if devices.count() == 0:
    return http.HttpResponseRedirect(goto)

  if devices.count() == 1:
    q = http.QueryDict(mutable=True)
    q.update({mfa_settings.MFA_REDIRECT_FIELD: goto})

    goto = reverse('django_2fa:verify', args=(str(devices[0].id),)) + '?' + q.urlencode()
    return http.HttpResponseRedirect(goto)

  context = {'devices': devices, 'next_field': mfa_settings.MFA_REDIRECT_FIELD, 'next': goto}
  return TemplateResponse(request, '2fa/login.html', context, status=207)


@login_required
def login_2fa_verify(request, device=None):
  device = get_object_or_404(Device, id=device, owner=request.user)
  form = MFAForm(device, request.POST or None)
  goto = request.GET.get(mfa_settings.MFA_REDIRECT_FIELD, settings.LOGIN_REDIRECT_URL)

  if request.method == 'GET':
    if device.device_type == 'email':
      device.send_code()

  if request.method == 'POST':
    goto = request.POST.get(mfa_settings.MFA_REDIRECT_FIELD, goto)

    if form.is_valid():
      request.session['2fa_verfied'] = request.user.id
      return http.HttpResponseRedirect(goto)

  context = {'form': form, 'device': device, 'next': goto, 'next_field': mfa_settings.MFA_REDIRECT_FIELD}
  if device.device_type == 'hkey':
    return TemplateResponse(request, '2fa/verify-fido.html', context, status=207)

  return TemplateResponse(request, '2fa/verify.html', context, status=207)


@login_required
def devices_list(request, response_type="html"):
  devices = Device.objects.filter(owner=request.user).order_by('name')
  if response_type == 'json':
    ret = {'devices': [d.to_dict() for d in devices]}
    return http.JsonResponse(ret)

  return TemplateResponse(request, '2fa/devices.html', {'devices': devices})


@mfa_login_required
def device_add(request, response_type="html"):
  form = AddDeviceForm(request.user, request.POST or None)
  goto = request.GET.get(mfa_settings.MFA_REDIRECT_FIELD, reverse('django_2fa:devices'))

  if request.method == 'POST':
    goto = request.POST.get(mfa_settings.MFA_REDIRECT_FIELD, goto)

    if form.is_valid():
      q = http.QueryDict(mutable=True)
      q.update({mfa_settings.MFA_REDIRECT_FIELD: goto})

      device = form.save()
      if device.device_type in ['email', 'app']:
        device.secret = pyotp.random_base32()
        device.save()

      goto = reverse('django_2fa:device-complete', args=(str(device.id),)) + "?" + q.urlencode()
      if response_type == 'json':
        return http.JsonResponse(device.to_dict())

      return http.HttpResponseRedirect(goto)

    elif response_type == 'json':
      return http.JsonResponse({'errors': form.errors.as_json()}, status_code=400)

  context = {'form': form, 'next': goto, 'next_field': mfa_settings.MFA_REDIRECT_FIELD}
  return TemplateResponse(request, '2fa/add-device.html', context)


@csrf_exempt
def device_add_json(request):
  return device_add(request, response_type="json")


@mfa_login_required
def device_complete(request, device=None, response_type="html"):
  device = get_object_or_404(Device, id=device, owner=request.user, setup_complete=False)
  goto = request.GET.get(mfa_settings.MFA_REDIRECT_FIELD, reverse('django_2fa:devices'))

  form = MFAForm(device, request.POST or None)
  if request.method == 'GET':
    if device.device_type == 'email':
      device.send_code()

  else:
    goto = request.POST.get(mfa_settings.MFA_REDIRECT_FIELD, goto)

    if form.is_valid():
      device.setup_complete = True
      device.save()
      request.session['2fa_verfied'] = request.user.id

      if response_type == 'json':
        return http.JsonResponse(device.to_dict())

      return http.HttpResponseRedirect(goto)

    elif response_type == 'json':
      return http.JsonResponse({'errors': form.errors.as_json()}, status_code=400)

  context = {'device': device, 'complete_setup': True, 'form': form, 'next': goto, 'next_field': mfa_settings.MFA_REDIRECT_FIELD}
  if device.device_type == 'hkey':
    return TemplateResponse(request, '2fa/complete-fido.html', context)

  if response_type == 'json':
    return http.JsonResponse({'status': 'Code Sent'})

  return TemplateResponse(request, '2fa/verify.html', context)


@csrf_exempt
def device_complete_json(request, device=None):
  return device_complete(request, device=device, response_type="json")


@mfa_login_required
def device_remove(request, device=None, response_type="html"):
  device = get_object_or_404(Device, id=device, owner=request.user)
  device.delete()
  goto = reverse('django_2fa:devices')

  if response_type == 'json':
    return http.JsonResponse({"status": "deleted"})

  return http.HttpResponseRedirect(goto)


def mfa_request(request, token):
  try:
    mrequest = MFARequest.get_from_token(token)

  except:
    raise http.Http404

  if request.user.is_authenticated and request.user.id == mrequest.owner.id:
    try:
      del request.session['2fa_verfied']

    except KeyError:
      pass

  else:
    login(request, mrequest.owner)
    request.session['2fa_logout'] = True

  goto = reverse('django_2fa:mfa-request-complete', args=[token])
  return http.HttpResponseRedirect(goto)


@mfa_login_required
def mfa_request_complete(request, token):
  try:
    mrequest = MFARequest.get_from_token(token, request.user)

  except:
    raise http.Http404

  mrequest.completed = True
  mrequest.save()

  if request.session.get('2fa_logout'):
    del request.session['2fa_logout']
    logout(request)

  context = {}
  return TemplateResponse(request, '2fa/request-completed.html', context)
