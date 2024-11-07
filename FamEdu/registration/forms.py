from django import forms
from .models import Child, Parent, Notification, School

class SchoolForm(forms.ModelForm):

    class Meta:
        model = School
        fields = ('number', 'type', 'city')

class ChildForm(forms.ModelForm):
    
    class Meta:
        model = Child
        fields = (
            'name', 'surname', 'patronymic', 'birthday', 'registration_address', 'living_address', 'phone'
        )
        widgets = {'birthday': forms.DateInput(attrs={'type': 'date'})}

class ParentForm(forms.ModelForm):

    class Meta:
        model = Parent
        fields = (
            'name', 'surname', 'patronymic', 'registration_address', 'living_address', 'phone', 'email'
        )

class NotificationForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(NotificationForm, self).__init__(*args, **kwargs)
        self.fields["applicant"].required = False
        self.fields["representative"].required = False
        self.fields["student"].required = False

    class Meta:
        model = Notification
        fields = ('applicant', 'representative', 'student', 'grade', 'prev_school', 'cur_school', 'note')


class NotificationReportForm(NotificationForm):

    def __init__(self, *args, **kwargs):
        super(NotificationReportForm, self).__init__(*args, **kwargs)
        self.fields['date'] = forms.DateField(label="Дата", widget=forms.DateInput(attrs={'type': 'date'}))
        for field_name in self.fields:
            field = self.fields[field_name]
            field.required = False


class SchoolReportForm(SchoolForm):

    def __init__(self, *args, **kwargs):
        super(SchoolReportForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.required = False

class ParentReportForm(ParentForm):

    def __init__(self, *args, **kwargs):
        super(ParentReportForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.required = False

class ChildReportForm(ChildForm):
    def __init__(self, *args, **kwargs):
        super(ChildReportForm, self).__init__(*args, **kwargs)
        for field_name in self.fields:
            field = self.fields[field_name]
            field.required = False