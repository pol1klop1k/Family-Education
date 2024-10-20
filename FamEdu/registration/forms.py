from django import forms
from .models import Child, Parent, Notification

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

    #add_applicant = forms.BooleanField(label="Добавить родителя")
    #add_representative = forms.BooleanField(label="Добавить второго родителя")
    #add_student = forms.BooleanField(label="Добавить ребенка")
    class Meta:
        model = Notification
        fields = ('applicant', 'representative', 'student', 'grade', 'prev_school', 'cur_school', 'note')
        requireds = {'applicant': False}