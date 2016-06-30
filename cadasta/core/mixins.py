from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _
from jsonattrs.models import Schema

from tutelary import mixins


class PermissionRequiredMixin(mixins.PermissionRequiredMixin):
    def handle_no_permission(self):
        msg = super().handle_no_permission()
        messages.add_message(self.request, messages.WARNING,
                             msg[0] if len(msg) > 0 and len(msg[0]) > 0
                             else _("PERMISSION DENIED"))
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


class LoginPermissionRequiredMixin(PermissionRequiredMixin,
                                   mixins.LoginPermissionRequiredMixin):
    pass


class JsonAttrsMixin:
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        obj = self.object
        field = self.attributes_field
        obj_attrs = getattr(obj, field)

        schemas = Schema.objects.from_instance(obj)
        attrs = [a for s in schemas for a in s.attributes.all()]
        context[field] = [(a.long_name, obj_attrs.get(a.name, '—'))
                          for a in attrs if not a.omit]
        return context
