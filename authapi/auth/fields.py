from rest_framework.serializers import Field


def GroupOneToOneBooleanField(model):
    class OneToOneBooleanField(Field):
        def to_representation(self, obj):
            if model.objects.filter(group=obj).exists():
                return True
            return False
        def to_internal_value(self, data):
            if data:
                model.objects.get_or_create(group=obj)
            else:
                model.objects.filter(group=obj).delete()
            return data

    return OneToOneBooleanField
