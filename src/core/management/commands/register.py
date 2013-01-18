from datetime import datetime

from django.core.management import BaseCommand
from django.contrib.auth.models import User

from core.models import Employee, EmployeeTracking


class Command(BaseCommand):
    args = '<username>'
    help = ''

    requires_model_validation = True

    def handle(self, *args, **kwargs):
        employee = Employee.objects.get(user__username=args[0])

        ets = EmployeeTracking.objects.filter(
            employee=employee,
            record_out__isnull=True
        )
        for et in ets:
            record_out = raw_input('[{}] SAIDA: '.format(et.record_in.strftime('%d/%m/%Y'))).split(':')
            record_out = et.record_in.replace(
                hour   = int(record_out[0]),
                minute = int(record_out[1])
            )

            et.record_out = record_out
            et.save()

        try:
            ets = EmployeeTracking.objects.get(
                employee=employee,
                record_in__startswith=datetime.today().date()
            )
        except EmployeeTracking.DoesNotExist:
            record_in = raw_input('[{}] ENTRADA: '.format(datetime.today().date().strftime('%d/%m/%Y'))).split(':')
            record_in = datetime.today().replace(
                hour   = int(record_in[0]),
                minute = int(record_in[1])
            )

            EmployeeTracking.objects.create(
                employee=employee,
                record_in=record_in
            )
