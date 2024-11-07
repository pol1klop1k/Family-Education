from django.shortcuts import render
from django.http import HttpResponse
from formtools.wizard.views import SessionWizardView
from .forms import ChildForm, ParentForm, NotificationForm, NotificationReportForm, SchoolReportForm, ParentReportForm, ChildReportForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic.base import TemplateView, View
from .report import ReportView
from .models import Notification


class NotificationReportView(ReportView):
    template_name = "registration_app/report_form.html"
    form_classes = {
        'notification': NotificationReportForm,
        'cur_school': SchoolReportForm,
        'applicant': ParentReportForm,
        'student': ChildReportForm,
    }
    main = 'notification'
    
    class Meta:
        model = Notification
        fields = ('date', 'applicant', 'representative', 'student', 'cur_school',)
        
class RegistrationMenuView(TemplateView):
    template_name = "registration_app/index.html"

def show_step_form(field):
    def inner(wizard):
        cleaned_data = wizard.get_cleaned_data_for_step('0') or dict()
        return not cleaned_data.get(field) 
    return inner

# Create your views here.
class RegistrationWizardView(LoginRequiredMixin, SessionWizardView):
    form_list = [NotificationForm, ParentForm, ParentForm, ChildForm]
    template_name = 'registration_app/new_notification.html'
    condition_dict = {
        "1": show_step_form("applicant"),
        "2": show_step_form("representative"),
        "3": show_step_form("student"),
    }

    def done(self, form_list, form_dict, **kwargs):
        notification_form = form_dict['0']
        notification = notification_form.save(commit=False)
        if not notification_form.cleaned_data.get('applicant'):
            applicant = form_dict['1'].save()
            notification.applicant = applicant
        if not notification_form.cleaned_data.get('representative'):
            representative = form_dict['2'].save()
            notification.representative = representative
        if not notification_form.cleaned_data.get('student'):
            student = form_dict['3'].save()
            print(student)
            notification.student = student
        notification.save()
        return HttpResponse("Form submitted!")
    
    def get_context_data(self, form, **kwargs):
        titles = {
            "0": "Уведомление",
            "1": "Заявитель",
            "2": "Второй представитель",
            "3": "Обучающийся",
        }
        context = super().get_context_data(form=form, **kwargs)
        context.update({'step_title': titles[self.steps.current]})
        return context