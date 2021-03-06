from dataforms.admin.forms import FieldAdminForm
from dataforms.models import Field, DataForm
from dataforms.app_settings import ADMIN_JS, ADMIN_CSS
from django.contrib import admin
from inlines import ChoiceInline, FieldInline


class FieldMappingAdmin(admin.ModelAdmin):
    list_display = ('id', 'dataform_slug', 'field_slug', 'field_label', 'order')
    list_filter = ('data_form',)
    list_editable = ('order',)
    search_fields = ('data_form__title', 'field__slug', 'field__label')
    list_select_related = True

    def __init__(self, *args, **kwargs):
        super(FieldMappingAdmin, self).__init__(*args, **kwargs)
        self.field_qs = Field.objects.all()
        self.dataform_qs = DataForm.objects.all()

    def dataform_slug(self, obj):
        return '%s' % filter(lambda d: d.id == obj.data_form_id, self.dataform_qs)[0].slug

    def field_slug(self, obj):
        return '%s' % filter(lambda f: f.id == obj.field_id, self.field_qs)[0].slug

    def field_label(self, obj):
        return '%s' % filter(lambda f: f.id == obj.field_id, self.field_qs)[0].label

    class Media:
        js = ADMIN_JS
        css = { 'all' : ADMIN_CSS }


class FieldAdmin(admin.ModelAdmin):
    list_select_related = True
    list_filter = ('dataform__title', 'field_type', 'visible', 'required',)
    list_display_links = ('label',)
    list_display = ('label', 'slug', 'field_type', 'visible', 'required', 'choices_link')
    list_editable = ('field_type', 'visible', 'required',)
    search_fields = ('label','slug')
    #inlines = [ChoiceInline, FieldInline]
    #inlines = [ChoiceInline]
    save_as = True
    form = FieldAdminForm

    def __init__(self, *args, **kwargs):
        super(FieldAdmin, self).__init__(*args, **kwargs)
        self.form.admin_site = self.admin_site

    def choices_link(self, obj):
        return '<a href="../fieldchoice/?field__id__exact=%s">Choices<a>' % obj.pk
    choices_link.allow_tags = True
    choices_link.short_description = "Choices"

    class Media:
        js = ADMIN_JS
        css = { 'all' : ADMIN_CSS }

