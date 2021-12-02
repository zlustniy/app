from dj_model_utils.mixins.approx import ApproxCountPaginatorMixin
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from las.mixins import DisablePreselectMixin, DisableModifyMixin
from las.models import (
    User,
    AccumulationRegister,
    ActionType,
    ExternalActionProcess,
    Instance,
    LiabilitiesType,
    SubjectAccumulation,
)


@admin.register(User)
class OverrideUserAdmin(UserAdmin):
    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if 'instance' not in fieldsets[0][1]['fields']:
            fieldsets[0][1]['fields'] += ('instance',)
        return fieldsets

    def get_list_display(self, request):
        list_display = super().get_list_display(request=request)
        list_display += ('instance',)
        return list_display


@admin.register(AccumulationRegister)
class AccumulationRegisterAdmin(
    ApproxCountPaginatorMixin,
    DisablePreselectMixin,
    DisableModifyMixin,
    admin.ModelAdmin,
):
    list_display = [
        'user',
        'liabilities_type',
        'receipt_number',
        'amount_record',
        'amount_total',
        'get_subject_ogrn',
    ]
    search_fields = [
        'id',
        'receipt_number',
        'subject__ogrn',
    ]
    list_filter = [
        'user__username',
        'user__instance__name',
    ]

    def get_subject_ogrn(self, obj):
        return obj.subject.ogrn

    get_subject_ogrn.short_description = 'ОГРН'
    get_subject_ogrn.admin_order_field = 'subject__ogrn'


@admin.register(ActionType)
class ActionTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(ExternalActionProcess)
class ExternalActionProcessAdmin(admin.ModelAdmin):
    pass


@admin.register(Instance)
class InstanceAdmin(admin.ModelAdmin):
    pass


@admin.register(LiabilitiesType)
class LiabilitiesTypeAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'get_instance',
        'postfix',
        'type_running',
        'is_default',
    ]
    search_fields = [
        'name',
    ]
    list_filter = [
        'instance__name',
    ]

    def get_instance(self, obj):
        return obj.instance.name

    get_instance.short_description = 'Инстанция'
    get_instance.admin_order_field = 'instance__name'


@admin.register(SubjectAccumulation)
class SubjectAccumulationAdmin(
    ApproxCountPaginatorMixin,
    DisablePreselectMixin,
    admin.ModelAdmin,
):
    list_display = [
        'ogrn',
        'name',
    ]
    search_fields = [
        'ogrn',
        'name',
    ]
    readonly_fields = [
        'ogrn',
    ]
