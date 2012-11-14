from datetime import date, datetime

from django import forms
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required

from core.models import Employee, EmployeeTracking

@login_required
def check(request):
    try:
        et = EmployeeTracking.objects.filter(employee__user=request.user).latest('record_in')
    except EmployeeTracking.DoesNotExist:
        return redirect('checkin', permanent=True)

    if et.is_checked_out:
        return redirect('checkin', permanent=True)
    return redirect('checkout', permanent=True)

@login_required
def checkIn(request):
    if request.method == 'POST':
        et = EmployeeTracking.objects.create(
            record_in = datetime.now(),
            employee = Employee.objects.get(user=request.user)
        )
        return redirect('check', permanent=True)
    return render(request, 'core_checkin.html')

@login_required
def checkOut(request):
    if request.method == 'POST':
        et = EmployeeTracking.objects.filter(employee__user=request.user).latest('record_in')
        et.record_out = datetime.now()
        et.save()
        return redirect('check', permanent=True)
    return render(request, 'core_checkout.html')
