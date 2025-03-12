from import_export import resources, widgets
from .models import Notification
from django.http import HttpResponse
from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from import_export.fields import Field
import openpyxl
from io import BytesIO

def openxlsx(dataset):
     workbook_data = BytesIO(dataset)
     workbook_data.seek(0)
     wb = openpyxl.load_workbook(workbook_data)
     return wb

def closexlsx(wb):
    output = BytesIO()
    wb.save(output)
    dataset = output.getvalue()
    return dataset


class Exporter(resources.ModelResource):

    def translate(self, queryset):
        dataset = super().export(queryset).xlsx
        
        wb = openxlsx(dataset)
        main = wb.worksheets[0]
        main.title = "Отчет"

        for column_cells in main.columns:
            length = max(len(str(cell.value)) for cell in column_cells) * 1.1
            main.column_dimensions[column_cells[0].column_letter].width = length

        dataset = closexlsx(wb)
        return dataset

    def export(self, queryset):
        dataset = self.translate(queryset)
        
        response = HttpResponse(dataset)
        response["Content-Disposition"] = 'attachment; filename="Otchet.xlsx"'
        return response
    
    

class ExportNotifications(Exporter):

    date = Field('date', 'Дата', widgets.DateWidget(coerce_to_string=False))
    student = Field('student__credentials', 'Обучающийся')
    cur_school = Field('cur_school__title', 'Место прикрепления')
    grade = Field('grade', 'Класс')

    class Meta:
        model = Notification
        fields = ('date', 'student', 'cur_school', 'grade')

class ExportTypeSchoolNotifications(ExportNotifications):
    
    def translate(self, queryset):
        dataset_online = super().translate(queryset["online"])
        dataset_offline = super().translate(queryset["offline"])
        wb_online = openxlsx(dataset_online)
        wb_offline = openxlsx(dataset_offline)
        offline_sheet = wb_offline.active
        offline_sheet.title = "Муниципальные"
        offline_sheet._parent = wb_online
        wb_online._add_sheet(offline_sheet)
        wb_online.worksheets[0].title = "Онлайн"

        new_dataset = closexlsx(wb_online)
        return new_dataset

class ExportGradeNotifications(ExportNotifications):
    pass

class ExportSchoolNotifications(ExportNotifications):
    pass
