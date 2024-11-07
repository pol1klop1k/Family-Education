from import_export import resources
from .models import Notification
from django.http import HttpResponse

class Exporter(resources.ModelResource):

    def export(self):
        dataset = super().export(self.main_queryset).csv
        response = HttpResponse(dataset)
        response["Content-Disposition"] = 'attachment; filename="report.xls"'
        return response
    

class ExportNotifications(resources.ModelResource):

    class Meta:
        model = Notification
        fields = ('date', 'applicant', 'representative', 'student', 'cur_school',)
