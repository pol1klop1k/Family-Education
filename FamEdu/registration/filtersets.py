from django_filters import FilterSet, DateFilter, CharFilter
from django import forms
from .models import Notification
from . import export
import re
from django.core.exceptions import ValidationError

class SchoolTypeFilterSet(FilterSet):
    exporter = export.ExportTypeSchoolNotifications()

    date_gte = DateFilter(field_name="date", lookup_expr="gte", label="С", widget=forms.DateInput(format=('%d.%m.%Y'), attrs={'type': 'date'}))
    date_lt = DateFilter(field_name="date", lookup_expr="lt", label="По", widget=forms.DateInput(format=('%d.%m.%Y'), attrs={'type': 'date'}))

    @property
    def qs(self):
        qs = super().qs
        online = qs.filter(cur_school__type="Онлайн")
        offline = qs.filter(cur_school__type="Муниципалитет")
        return {"online": online, "offline": offline}

    class Meta:
        model = Notification
        fields = ('date_gte', 'date_lt', )

class GradeFilterSet(FilterSet):
    exporter = export.ExportGradeNotifications()

    def grade_validator(value):
        if re.fullmatch(r"\A\d+\Z|\A\d+-\d+\Z", value):
            for num in value.split("-"):
                try:
                    grade = int(num)
                    if grade > 11 or grade < 1:
                        raise ValidationError(("Класс должен быть в диапазоне от 1 до 11"))
                except ValueError:
                    raise ValidationError(("Класс должен быть числом"))
        else:
            raise ValidationError(("Введите корректный формат класса"))


    date_gt = DateFilter(field_name="date", lookup_expr="gte", label="С", widget=forms.DateInput(attrs={'type': 'date'}))
    date_lt = DateFilter(field_name="date", lookup_expr="lt", label="По", widget=forms.DateInput(attrs={'type': 'date'}))
    grade = CharFilter(field_name="grade", validators=[grade_validator], method='grade_filter')

    def grade_filter(self, queryset, name, value):
        if "-" in value:
            bottom, up = value.split("-")
            return queryset.filter(**{
                f"{name}__lte": up, 
                f"{name}__gte": bottom,})
        return queryset.filter(**{
            name: value,
        })

    class Meta:
        model = Notification
        fields = ('date_gt', 'date_lt', 'grade',)


class SchoolFilterSet(FilterSet):
    exporter = export.ExportSchoolNotifications()

    date = DateFilter(field_name="date", widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Notification
        fields = ('date', 'cur_school', )