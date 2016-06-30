"""
TEMPORARY - THIS MUST BE REMOVED ONCE THE BUG IN JSONATTRS IS FIXED
"""

from jsonattrs.forms import AttributeModelForm as JsonModelForm
from django.contrib.contenttypes.models import ContentType
from jsonattrs.models import Schema, compose_schemas
from jsonattrs.forms import form_field_from_name


class AttributeModelForm(JsonModelForm):
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
