from core.forms import AttributeModelForm

from .models import Party, TenureRelationship, TenureRelationshipType


class PartyForm(AttributeModelForm):
    attributes_field = 'attributes'

    class Meta:
        model = Party
        fields = ['name', 'type']

    def __init__(self, project_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id

    def save(self):
        tf = self.fields['type']
        initial = self.initial['type']
        data = self.data['type']
        if initial and data:
            if (tf.has_changed(initial, data)):
                self.instance.name = self.data['name']
                self.instance.type = self.data['type']
                self.instance.attributes = {}
                # instance = super().save(commit=True)
                self.instance.save()
                return None
        else:
            instance = super().save(commit=False)
            instance.project_id = self.project_id
            instance.save()
            return instance


class TenureRelationshipEditForm(AttributeModelForm):
    attributes_field = 'attributes'

    class Meta:
        model = TenureRelationship
        fields = ['tenure_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tenure_types = TenureRelationshipType.objects.values_list('id',
                                                                  'label')
        self.fields['tenure_type'].choices = tenure_types

    def save(self):
        return super().save()
