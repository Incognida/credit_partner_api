from django.contrib import admin
from .models import Form, Offer, Proposal


def get_model_search_fields(model_name):
    model = globals()[model_name]
    fields = []
    for field in model._meta.get_fields():
        if field.one_to_many:
            continue
        if field.is_relation:
            fields.append(field.name + "__pk")
        else:
            fields.append(field.name)
    return fields


class get_model_list_filter:
    def __init__(self):
        self._reused = False

    def __call__(self, model_name):
        model = globals()[model_name]
        fields = []
        self._reused = True
        for field in model._meta.get_fields():
            if self._reused and field.name == 'id':
                continue
            if field.one_to_many:
                continue
            if field.is_relation and field.name.startswith('user'):
                if 'user_id' not in fields:
                    fields.append('user__id')
                if 'user__username' not in fields:
                    fields.append('user__username')
            elif field.is_relation:
                related_model = field.related_model()
                related_fields = self(related_model.__class__.__name__)

                fields.append(field.name + '__id')
                fields.append(related_fields)
            else:
                fields.append(field.name)
        return fields


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    get_custom_list_filter = get_model_list_filter()
    list_display = [field.name for field in Form._meta.get_fields() if not field.one_to_many]
    raw_id_fields = ('user',)
    search_fields = get_model_search_fields('Form')
    list_filter = get_custom_list_filter('Form')


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    get_custom_list_filter = get_model_list_filter()
    list_display = [field.name for field in Offer._meta.get_fields() if not field.one_to_many]
    raw_id_fields = ('user',)
    search_fields = get_model_search_fields('Offer')
    list_filter = get_custom_list_filter('Offer')


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    get_custom_list_filter = get_model_list_filter()
    list_display = [field.name for field in Proposal._meta.get_fields() if not field.one_to_many]
    raw_id_fields = ('form', 'offer')
    search_fields = get_model_search_fields('Proposal')
    list_filter = [field.name for field in Proposal._meta.get_fields() if not field.one_to_many]
