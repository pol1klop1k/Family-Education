from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Prefetch
from .export import Exporter, ExportNotifications

class ReportView(TemplateView, Exporter):
    ''' template_name - имя шаблона
        form_classes - словарь, ключ-имя внешнего ключа или мейн таблички, значение-форма для обработки
        main - строка, должна совпадать с названием ключа мейн таблички, для которой строится отчет
    ''' 

    def __init__(self, *args, **kwargs):
        self.forms = {k:v(prefix=k) for k,v in self.form_classes.items()}
        self.prefetches = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for form in self.forms:
            context[f"{form}_form"] = self.forms[form]
        return context

    def populate(self, request, *args, **kwargs):
        invalid = False
        self.filters = dict()
        self.main_queryset = self.form_classes[self.main].Meta.model.objects.filter()

        for model in self.form_classes:
            form_class = self.form_classes[model]
            cur = form_class(request.POST, prefix=model)
            self.forms[model] = cur

            if not cur.is_valid():
                invalid = True
            else:
                filter = {k:v for k,v in cur.cleaned_data.items() if v!= None and v != ""}
                queryset = cur.Meta.model.objects.filter(**filter)
                if model != self.main:
                    if filter:
                        self.filters[f"{model}__in"] = queryset
                        self.prefetches.append(Prefetch(model, queryset))
                else:
                    self.main_queryset = queryset

        return invalid

    def post(self, request, *args, **kwargs):

        invalid = self.populate(request)
        if invalid:
            return self.render_to_response(self.get_context_data())
        for prefetch in self.prefetches:
            self.main_queryset = self.main_queryset.prefetch_related(prefetch)
        self.main_queryset = self.main_queryset.filter(**self.filters)
        response = self.export()
        #return HttpResponse(render(self.request, "registration_app/report.html", context={"reported_records": self.main_queryset}))
        return response