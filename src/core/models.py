from datetime import date

from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.contrib.auth.models import User


class Employee(models.Model):
    user = models.OneToOneField(User)
    full_name = models.CharField(max_length=200)
    workload_days  = models.CommaSeparatedIntegerField(max_length=13)
    workload_hours = models.FloatField()

    @property
    def workload_minutes(self):
        return self.workload_hours * 60

    @property
    def total_days(self):
        return EmployeeTracking.objects.filter(employee=self).count()

    @property
    def total_hours(self):
        return round(EmployeeTotalHours.objects.get(employee=self).total_hours, 2)

    @property
    def last_checkin(self):
        return EmployeeTracking.objects.filter(employee=self).latest('record_in')

    @property
    def last_checkout(self):
        return EmployeeTracking.objects.filter(employee=self).latest('record_out')

    def save(self):
        self.user.first_name = self.full_name.split(' ')[0]
        self.user.last_name  = self.full_name.split(' ')[-1]
        self.user.save()

        super(Employee, self).save()

        try:
            self.employeetotalhours_set.get()
        except EmployeeTotalHours.DoesNotExist:
            EmployeeTotalHours.objects.create(employee=self)

    def __unicode__(self):
        return self.full_name


class EmployeeTracking(models.Model):
    record_in = models.DateTimeField()
    record_out = models.DateTimeField(blank=True, null=True)
    worked_hours = models.FloatField(blank=True, default=0)

    employee = models.ForeignKey(Employee)

    @property
    def worked_minutes(self):
        return self.worked_hours * 60

    @property
    def is_checked_out(self):
        if self.record_out:
            return True
        return False

    def __unicode__(self):
        return self.record_in.strftime('%H:%M %d/%m/%Y')

    class Meta:
        unique_together = ('record_in', 'record_out', 'employee')


class EmployeeTotalHours(models.Model):
    total_hours = models.FloatField(blank=True, default=0)

    employee = models.ForeignKey(Employee, unique=True)

    def __unicode__(self):
        return str(self.total_hours)


def employee_tracking_update(sender, **kwargs):
    et = kwargs['instance']
    et.record_in = et.record_in.replace(second=0)

    if not et.record_out:
        et.worked_hours = 0
    else:
        employee = et.employee
        eth = employee.employeetotalhours_set.get()

        et.record_in = et.record_in.replace(second=0, microsecond=0)
        et.record_out = et.record_out.replace(second=0, microsecond=0)
        et.worked_hours = (et.record_out - et.record_in).seconds / 3600.0
        et.worked_hours = round(et.worked_hours, 2)
        eth.total_hours = eth.total_hours + et.worked_hours
        eth.save()

    post_save.disconnect(employee_tracking_update, sender=EmployeeTracking)
    et.save()
    post_save.connect(employee_tracking_update, sender=EmployeeTracking)
post_save.connect(employee_tracking_update, sender=EmployeeTracking)


def employee_tracking_delete(sender, **kwargs):
    et = kwargs['instance']

    if et.record_out:
        employee = et.employee

        try:
            eth = employee.employeetotalhours_set.get()

            et.worked_hours = (et.record_out - et.record_in).seconds / 3600.0
            et.worked_hours = round(et.worked_hours, 2)
            eth.total_hours = eth.total_hours - et.worked_hours
            eth.save()
        except EmployeeTotalHours.DoesNotExist:
            pass
post_delete.connect(employee_tracking_delete, sender=EmployeeTracking)
