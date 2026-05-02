from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

class ReportView(TemplateView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(self.forms)
        return context


class ReportListView(FormView):

    def get_form(self):
        return self.filterset.form

    def get(self, request, *args, **kwargs):
        self.report_type = kwargs['report_type']
        filterset_cls = self.filtersets[self.report_type]
        self.filterset = filterset_cls(self.request.GET, self.model.objects.all())
        response = super().get(request, *args, **kwargs)
        return response

    def get_template_names(self):
        return self.templates[self.report_type]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['qs'] = self.filterset.qs
        return context
    
    def post(self, request, *args, **kwargs):
        self.report_type = kwargs['report_type']
        filterset_cls = self.filtersets[self.report_type]
        self.filterset = filterset_cls(self.request.GET, self.model.objects.all())
        response = self.filterset.exporter.export(self.filterset.qs)
        return response
