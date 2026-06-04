from rest_framework import serializers


class ExtractDataFromScanSerializer(serializers.Serializer):
    data_type = serializers.CharField()
    doc_data = serializers.CharField()

    def validate_doc_data(self, data: str):
        return data.encode('utf-8')


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
    title = serializers.CharField()


class StudentsListSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    lastName = serializers.CharField(source="surname")
    firstName = serializers.CharField(source="name")
    patronymic = serializers.CharField()
    fullName = serializers.CharField(source="*")
    regNumber = serializers.CharField(source="notification.id", default=None)
    grade = serializers.IntegerField(source="notification.grade", default=None)
    attestationSchool = serializers.CharField(source="notification.cur_school", default=None)
    homeschoolingSince = serializers.IntegerField(source="notification.date.year", default=None)
    isArchived = serializers.BooleanField(default=False)
    prevSchool = serializers.CharField(source="notification.prev_school", default=None)
    phone = serializers.CharField()
    address = serializers.CharField(source="living_address")
    notes = serializers.CharField(source="notification.note", default=None)


class StudentRetrieveSerializer(StudentsListSerializer):
    birthday = serializers.DateField()
    registrationAddress = serializers.CharField(source="living_address")
    livingAddress = serializers.CharField(source="living_address")


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
