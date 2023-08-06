class Default:
    def __init__(self, instance):
        self.instance = instance

    @property
    def data(self):
        return self.to_representation(self.instance)

    def to_representation(self, instance):
        data = {}
        for field in instance._meta.get_fields():
            if field.is_relation:
                try:
                    data[field.name] = field.value_to_string(instance)
                except AttributeError:
                    data[field.name] = str(field)
            else:
                data[field.name] = str(getattr(instance, field.name))

        return data
