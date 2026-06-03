from rest_framework import serializers


class ExtractDataFromScanSerializer(serializers.Serializer):
    data_type = serializers.CharField()
    doc_data = serializers.CharField()

    def validate_doc_data(self, data: str):
        return data.encode('utf-8')
