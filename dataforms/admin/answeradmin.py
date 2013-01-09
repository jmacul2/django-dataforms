from dataforms.models import AnswerChoice
from django.contrib import admin


class AnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'submission', 'data_form', 'field', 'field_type', 'value', 'choices')
    #inlines = [AnswerTextInline, AnswerNumberInline, AnswerChoiceInline]
    list_select_related = True

    search_fields = ('field__slug', 'field__label')

    def __init__(self, *args, **kwargs):
        super(AnswerAdmin, self).__init__(*args, **kwargs)
        self.answer_choices_qs = AnswerChoice.objects.select_related('answer', 'choice').all()

    def queryset(self, request):
        qs = super(AnswerAdmin, self).queryset(request)

        # use prefetch_related if we can
        if hasattr(qs, 'prefetch_related'):
            return qs.prefetch_related('choice')
        else:
            return qs

    # Get Choices
    def choices(self, obj):
        return '%s' % str(obj.choice.all())

    # Get Field Types
    def field_type(self, obj):
        return '%s' % obj.field.field_type

    #Hide the model from view
#    def get_model_perms(self, request):
#        return {}


class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('id', '__unicode__', 'last_modified', 'answers_link')
    #list_filter = ('')
    search_fields = ('slug',)
    list_select_related = True

    def answers_link(self, obj):
        return '<a href="answers/%s/">Answers<a>' % obj.pk
    answers_link.allow_tags = True
    answers_link.short_description = "Fields"
