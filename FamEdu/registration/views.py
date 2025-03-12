"""Модуль представлений
"""

from typing import Any
from django.shortcuts import render
from django.http import HttpResponseRedirect
from formtools.wizard.views import SessionWizardView
from .forms import ChildForm, ParentForm, NotificationForm, MunSchoolForm, SchoolTypeForm, OnlineSchoolForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic.base import TemplateView
from .report import ReportView, ReportListView
from .filtersets import SchoolTypeFilterSet, GradeFilterSet, SchoolFilterSet
from .models import Notification, School, Child, Parent
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views import View


class DirectoryMixin(View):

    """Миксин для справочников
    """

    models_slugs = {
    "school": School,
    "student": Child,
    "notification": Notification,
    "applicant": Parent,
    }

    fields = "__all__"

    def get(self, request, *args, **kwargs):
        if self.model is None:
            self.model = self.models_slugs[kwargs["entity"]]
        return super().get(request, *args, **kwargs)
    
    def post(self, request, *args, **kwargs):
         if self.model is None:
            self.model = self.models_slugs[kwargs["entity"]]
         return super().post(request, *args, **kwargs)
    

class DirectoryListView(DirectoryMixin, ListView):
    template_name = "registration_app/directories/directory_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = self.model._meta.verbose_name_plural
        return context
    

class DirectoryCreateView(DirectoryMixin, CreateView):
    template_name = "registration_app/directories/directory_create.html"

    def get_context_data(self, **kwargs):

        titles = {
            School: "школу",
            Child: "обучающегося",
            Notification: "уведомление",
            Parent: "заявителя",
        }

        context = super().get_context_data(**kwargs)
        context["title"] = titles[self.model]
        return context

class DirectoryUpdateView(DirectoryMixin, UpdateView):
    template_name = "registration_app/directories/directory_create.html"

    def get_context_data(self, **kwargs):

        titles = {
            School: "школу",
            Child: "обучающегося",
            Notification: "уведомление",
            Parent: "заявителя",
        }

        context = super().get_context_data(**kwargs)
        context["title"] = titles[self.model]
        return context

class DirectoryDetailView(LoginRequiredMixin, DirectoryMixin, DetailView):
    template_name = "registration_app/directories/directory_detail.html"

class NotificationReportListView(ReportListView):

    model = Notification
    
    templates = {
        "school_type": ["registration_app/reports/school_type_report.html"],
        "grade": ["registration_app/reports/grade_report.html"],
        "school": ["registration_app/reports/school_report.html"],
    }

    filtersets = {
        "school_type": SchoolTypeFilterSet,
        "grade": GradeFilterSet,
        "school": SchoolFilterSet,
    }


class NotificationReportView(ReportView):
    template_name = "registration_app/report_form.html"
    forms = {
        "school_type_form": SchoolTypeFilterSet([], Notification.objects.all()).form,
        "grade_form": GradeFilterSet([], Notification.objects.all()).form,
        "school_form": SchoolFilterSet([], Notification.objects.all()).form,
    }



class RegistrationMenuView(LoginRequiredMixin, TemplateView):
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
            notification.student = student
        notification.employee = self.request.user
        notification.save()
        return HttpResponseRedirect(reverse("registration:notification_detail", kwargs={"pk": notification.pk}))
    
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
    

class SchoolWizardView(LoginRequiredMixin, SessionWizardView):

    def condition(type):
        def inner(wizard):
            cleaned_data = wizard.get_cleaned_data_for_step('0') or dict()
            return cleaned_data.get("type") == type
        return inner

    form_list = [SchoolTypeForm, MunSchoolForm, OnlineSchoolForm,]
    template_name = 'registration_app/directories/new_school.html'
    condition_dict = {
        "1": condition("Муниципалитет"),
        "2": condition("Онлайн"),
    }


    def done(self, form_list, form_dict, **kwargs):
        type_form = form_dict["0"]
        type = type_form.cleaned_data.get("type")
        if type == "Муниципалитет":
            school_form = form_dict["1"]
        else:
            school_form = form_dict["2"]
        school = school_form.save(commit=False)
        school.type = type
        school.save()
        return HttpResponseRedirect(reverse("registration:directory_list", kwargs={"entity": "school",}))