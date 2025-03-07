from django import forms
from .models import Child, Parent, Notification, School


class MunSchoolForm(forms.ModelForm):

    class Meta:
        model = School
        fields = ('name', 'number', 'city')


class OnlineSchoolForm(forms.ModelForm):

    class Meta:
        model = School
        fields = ('online_title', )


class SchoolTypeForm(forms.Form):
    
    type = forms.ChoiceField(label='Тип', choices=[
        ("Муниципалитет", "Муниципалитет"), 
        ("Онлайн", "Онлайн")
    ])
        

class ChildForm(forms.ModelForm):
    
    class Meta:
        model = Child
        fields = (
            'surname', 'name', 'patronymic', 'birthday', 'registration_address', 'living_address', 'phone'
        )
        widgets = {'birthday': forms.DateInput(attrs={'type': 'date'})}

class ParentForm(forms.ModelForm):

    class Meta:
        model = Parent
        fields = (
            'surname', 'name', 'patronymic', 'registration_address', 'living_address', 'phone', 'email'
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