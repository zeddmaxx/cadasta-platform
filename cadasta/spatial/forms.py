from django import forms
from django.contrib.gis import forms as gisforms
from django.utils.translation import ugettext as _


from leaflet.forms.widgets import LeafletWidget
from jsonattrs.forms import AttributeModelForm

from core.util import ID_FIELD_LENGTH
from party.models import Party, TenureRelationship, TenureRelationshipType
from .models import SpatialUnit
from .widgets import SelectPartyWidget, NewEntityWidget

from django.contrib.contenttypes.models import ContentType
from jsonattrs.models import Schema, compose_schemas
from jsonattrs.forms import form_field_from_name


class LocationForm(AttributeModelForm):
    geometry = gisforms.GeometryField(widget=LeafletWidget())
    attributes_field = 'attributes'

    class Meta:
        model = SpatialUnit
        fields = ['geometry', 'type']

    def __init__(self, project_id=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project_id = project_id

    def add_attribute_fields(self, schema_selectors):
        attrs = None
        attrvals = getattr(self.instance, self.attributes_field)
        schemas = None
        if self.instance.pk:
            schemas = Schema.objects.from_instance(self.instance)
        elif schema_selectors is not None:
            selectors = []
            for ss in schema_selectors:
                selectors.append(ss['selector'])
                if ss['name'] is not None:
                    setattr(self.instance, ss['name'], ss['value'])
            content_type = ContentType.objects.get_for_model(self.Meta.model)
            schemas = Schema.objects.lookup(
                content_type=content_type, selectors=selectors
            )
            attrvals.setup_schema(schemas)
        attrs, _, _ = compose_schemas(*schemas)
        for name, attr in attrs.items():
            fieldname = self.attributes_field + '::' + name
            atype = attr.attr_type
            args = {'label': attr.long_name}
            field = form_field_from_name(atype.form_field)
            if atype.form_field == 'CharField':
                args['max_length'] = 32
            if (atype.form_field == 'ChoiceField' or
               atype.form_field == 'MultipleChoiceField'):
                args['choices'] = list(map(lambda c: (c, c), attr.choices))
            if atype.form_field == 'BooleanField':
                args['required'] = False
                if len(attr.default) > 0:
                    args['initial'] = (attr.default != 'False')
            elif attr.required:
                args['required'] = True
                if len(attr.default) > 0:
                    args['initial'] = attr.default
            self.set_initial(args, name, attr, attrvals)
            self.fields[fieldname] = field(**args)

    def save(self):
        instance = super().save(commit=False)
        instance.project_id = self.project_id
        instance.save()
        return instance


REL_TYPE_CHOICES = (
    ('', 'Please select'),
    ('L', 'Location'),
    ('P', 'Party')
)


class TenureRelationshipForm(forms.Form):
    id = forms.CharField(
        required=False,
        max_length=ID_FIELD_LENGTH)
    new_entity = forms.BooleanField(required=False, widget=NewEntityWidget())
    name = forms.CharField(required=False, max_length=200)
    party_type = forms.ChoiceField(choices=Party.TYPE_CHOICES)
    tenure_type = forms.ChoiceField(choices=[])

    class Media:
        js = ('/static/js/rel_tenure.js',)

    def __init__(self, project, spatial_unit, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id'].widget = SelectPartyWidget(project.id)
        tenure_types = TenureRelationshipType.objects.values_list('id',
                                                                  'label')
        self.fields['tenure_type'].choices = tenure_types
        self.project = project
        self.spatial_unit = spatial_unit

    def clean_id(self):
        new_entity = self.data.get('new_entity', None)
        id = self.cleaned_data.get('id', '')

        if not new_entity and not id:
            raise forms.ValidationError(_("This field is required."))
        return id

    def clean_name(self):
        new_entity = self.cleaned_data.get('new_entity', None)
        name = self.cleaned_data.get('name', None)

        if new_entity and not name:
            raise forms.ValidationError(_("This field is required."))
        return name

    def save(self):
        if self.cleaned_data['new_entity']:
            party = Party.objects.create(
                name=self.cleaned_data['name'],
                type=self.cleaned_data['party_type'],
                project=self.project
            )
        else:
            party = Party.objects.get(pk=self.cleaned_data['id'])

        t = TenureRelationship.objects.create(
            party=party,
            spatial_unit=self.spatial_unit,
            tenure_type_id=self.cleaned_data['tenure_type'],
            project=self.project
        )
        return t
