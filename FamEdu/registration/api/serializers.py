import re

from django.db import transaction
from rest_framework import serializers

from accounting.models import AccountingList
from registration.models import Child, Notification, Parent, School


class ExtractDataFromScanSerializer(serializers.Serializer):
    data_type = serializers.CharField()
    doc_data = serializers.CharField()

    def validate_doc_data(self, data: str):
        return data.encode('utf-8')


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fullName = serializers.CharField(source="*")
    position = serializers.CharField()
    email = serializers.CharField()


class SchoolSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    number = serializers.IntegerField()
    type = serializers.CharField()
    city = serializers.CharField()
    online_title = serializers.CharField()
    title = serializers.SerializerMethodField()

    def get_title(self, school: School):
        return school.online_title or str(school)


class ParentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fullName = serializers.CharField(source="*")
    phone = serializers.CharField()
    email = serializers.CharField()
    address = serializers.CharField(source="living_address")


class StudentsListSerializer(serializers.Serializer):
    id = serializers.IntegerField(source="student.id")
    lastName = serializers.CharField(source="student.surname")
    firstName = serializers.CharField(source="student.name")
    patronymic = serializers.CharField(source="student.patronymic")
    fullName = serializers.CharField(source="student")
    grade = serializers.IntegerField()
    regNumber = serializers.IntegerField(source="id")
    attestationSchool = serializers.CharField(source="cur_school")
    homeschoolingSince = serializers.IntegerField(source="date.year")
    isArchived = serializers.BooleanField(source="is_archived")
    prevSchool = serializers.CharField(source="prev_school")
    phone = serializers.CharField(source="student.phone")
    address = serializers.CharField(source="student.living_address")
    notes = serializers.CharField(source="note")
    parents = serializers.SerializerMethodField()
    birthday = serializers.DateField(source="student.birthday")


    def get_parents(self, notification):
        return [
            ParentSerializer(notification.applicant).data,
            ParentSerializer(notification.representative).data,
        ]


class StudentRetrieveSerializer(StudentsListSerializer):
    registrationAddress = serializers.CharField(source="student.living_address")
    livingAddress = serializers.CharField(source="student.living_address")


class NotificationSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    date = serializers.DateField()
    regNumber = serializers.IntegerField(source="id")
    grade = serializers.IntegerField()
    prevSchool = serializers.CharField(source="prev_school")
    curSchool = serializers.CharField(source="cur_school")
    applicant = serializers.CharField()
    representative = serializers.CharField()
    employee = serializers.CharField()
    note = serializers.CharField()


class ChildCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Child
        fields = (
            "surname", "name", "patronymic", "birthday", "registration_address",
            "living_address", "phone",
        )


class ParentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Parent
        fields = (
            "surname", "name", "patronymic", "registration_address",
            "living_address", "phone", "email",
        )


class NotificationCreateSerializer(serializers.Serializer):
    applicant = ParentCreateSerializer()
    representative = ParentCreateSerializer()
    student = ChildCreateSerializer()
    grade = serializers.IntegerField()
    prev_school = serializers.CharField()
    cur_school = serializers.CharField()
    note = serializers.CharField()

    @transaction.atomic
    def create(self, validated_data):
        applicant = Parent.objects.create(**validated_data["applicant"])
        representative = Parent.objects.create(**validated_data["representative"])
        student = Child.objects.create(**validated_data["student"])
        
        prev_school_val, cur_school_val = validated_data["prev_school"], validated_data["cur_school"]
        if prev_school_val.isdigit():
            prev_school = School.objects.get(pk=int(prev_school_val))
        else:
            prev_school = School.objects.create(online_title=prev_school_val, type="Онлайн")
        
        if cur_school_val.isdigit():
            cur_school = School.objects.get(pk=int(cur_school_val))
        else:
            cur_school = School.objects.create(online_title=cur_school_val, type="Онлайн")

        return Notification.objects.create(
            applicant=applicant,
            representative=representative,
            student=student,
            prev_school=prev_school,
            cur_school=cur_school,
            note=validated_data["note"],
            employee=self.context["employee"],
            grade=validated_data["grade"]
        )

class NotificationUpdateSerializer(serializers.ModelSerializer):

    applicant = serializers.CharField()
    representative = serializers.CharField()
    student = serializers.CharField()
    prev_school = serializers.CharField()
    cur_school = serializers.CharField()

    class Meta:
        model = Notification
        fields = (
            "applicant", "representative", "student", "grade", "prev_school",
            "cur_school", "note", "employee", "is_archived",
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        for i in ("applicant", "representative", "student"):
            fio = validated_data.pop(i, None)
            if fio is None:
                continue
            surname, name, patronymic = fio.split()
            person = getattr(instance, i)
            person.surname = surname
            person.name = name
            person.patronymic = patronymic
            person.save()
        for i in ("prev_school", "cur_school"):
            school_title: str | None = validated_data.pop(i, None)
            if school_title is None:
                continue

            if school_title.isdigit():
                setattr(instance, i, School.objects.get(pk=int(school_title)))
                continue

            match = re.match(r'(.+) №(\d+) (?:п\.|г\.|пос\.|ст\.)(.+)', school_title)
            if match is None:
                school, _ = School.objects.get_or_create(online_title=school_title, type="Онлайн")
            else:
                name, number, city = match.groups()
                school, _ = School.objects.get_or_create(
                    name=name,
                    number=number,
                    city=city,
                    type="Муниципалитет",
                )
            setattr(instance, i, school)

        return super().update(instance, validated_data)


class DocumentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    fileUrl = serializers.CharField(source="file.url")
    uploadedAt = serializers.SerializerMethodField()
    fileName = serializers.CharField(source="name")

    def get_uploadedAt(self, instance):
        return instance.uploaded_at.date()


class UploadDocumentSerializer(serializers.Serializer):
    doc = serializers.ImageField()
    name = serializers.CharField()


class AccountingListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    student = StudentRetrieveSerializer(source="notification")
    is_successed = serializers.BooleanField()
    school = SchoolSerializer()
    grade = serializers.IntegerField()
    study_year = serializers.CharField()
    mail_link = serializers.URLField()


class AccountingUpdateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = AccountingList
        fields = ('is_successed',)
