from datetime import date, datetime, timedelta

from django import forms
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from core.models import Employee, EmployeeTracking


@login_required
def checkIn(request):
    if request.method == 'POST':
        et = EmployeeTracking.objects.create(
            record_in = datetime.now(),
            employee = Employee.objects.get(user=request.user)
        )
    return redirect('home')

@login_required
def checkOut(request):
    if request.method == 'POST':
        et = EmployeeTracking.objects.filter(employee__user=request.user).latest('record_in')
        et.record_out = datetime.now()
        et.save()
    return redirect('home')

@login_required
def history(request, weekly=True, monthly=False, custom=False):
    ets = None
    if weekly:
        last_week = datetime.now().date() - timedelta(days=7)
        ets = EmployeeTracking.objects.filter(employee__user=request.user, record_out__gte=last_week)
    return render(request, 'core_history.html', {'ets': ets})

@login_required
def home(request):
    try:
        et = EmployeeTracking.objects.filter(employee__user=request.user).latest('record_in')
    except EmployeeTracking.DoesNotExist:
        return render(request, 'core_checkin.html')

    if et.is_checked_out:
        return render(request, 'core_checkin.html')
    return render(request, 'core_checkout.html')
