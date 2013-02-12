from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple, RelatedFieldWidgetWrapper
from django.db.models.fields.related import ForeignKey, ManyToOneRel, ManyToManyRel
from dataforms.models import Binding, Field, FieldChoice, DataFormField, Choice


class BindingAdminForm(forms.ModelForm):
    field_choice = forms.ModelChoiceField(
        queryset=FieldChoice.objects.select_related('field', 'choice').all(), required=False
    )
    true_field = forms.MultipleChoiceField(choices=[],
        widget=FilteredSelectMultiple("True Fields", is_stacked=True), required=False)
    true_choice = forms.MultipleChoiceField(choices=[],
        widget=FilteredSelectMultiple("True Choices", is_stacked=True), required=False)
    false_field = forms.MultipleChoiceField(choices=[],
        widget=FilteredSelectMultiple("False Fields", is_stacked=True), required=False)
    false_choice = forms.MultipleChoiceField(choices=[],
        widget=FilteredSelectMultiple("False Choices", is_stacked=True), required=False)

    additional_rules = forms.ModelMultipleChoiceField(queryset=Binding.objects.all(), required=False)

    def __init__(self, *args, **kwargs):
        super(BindingAdminForm, self).__init__(*args, **kwargs)

        self.fields['true_field'].choices = self.field_choices()
        self.fields['false_field'].choices = self.field_choices()
        self.fields['true_choice'].choices = self.choice_choices()
        self.fields['false_choice'].choices = self.choice_choices()


    def clean_additional_rules(self):
        data = ','.join([unicode(b.id) for b in self.cleaned_data['additional_rules']])
        return data

    def field_choices(self):
        return [
            (u'%s__%s' % (field.data_form, field.field), u'%s (%s)' % (field.data_form, field.field))
            for field in DataFormField.objects.select_related('data_form', 'field').all().order_by('data_form')
        ]

    def choice_choices(self):
        return [
            (u'%s__%s___%s' % (fc.data_form_slug, fc.field_slug, fc.choice_value),
             u'(%s) %s<br>(%s)' % (fc.data_form_slug, fc.field_slug, fc.choice_value.upper()))
            for fc in FieldChoice.objects.get_fieldchoice_data()
        ]

    class Meta:
        model = Binding


class FieldAdminForm(forms.ModelForm):
    choices = forms.MultipleChoiceField(required=False, help_text=None, choices=[])

    def __init__(self, *args, **kwargs):
        super(FieldAdminForm, self).__init__(*args, **kwargs)
        self.fields['choices'].widget = RelatedFieldWidgetWrapper(
                    FilteredSelectMultiple("Choices", is_stacked=False, choices=[self.choice_choices()]),
                    ManyToManyRel(Choice),
                    self.admin_site)
        self.fields['choices'].choices = self.choice_choices()

    class Meta:
        model = Field

    def clean_label(self):
        data = self.cleaned_data['label']

        if 'meta' in data:
            raise forms.ValidationError("You cannot use the term 'meta' as a label as it is reserved.")
        return data

    def save(self, *args, **kwargs):
        field = super(FieldAdminForm, self).save(commit=False)
        choices = self.cleaned_data['choices']
        del self.cleaned_data['choices']
        is_new = True if not hasattr(field, 'pk') else False
        field.save()

        # Clear all field choices
        if not is_new:
            field.choices.clear()
        #assert False
        for choice in choices:
            FieldChoice.objects.create(
                field=field,
                choice=Choice.objects.get(pk=choice)
            )

        return field

    def choice_choices(self):
        return [(choice.id, choice.title) for choice in Choice.objects.all()]


