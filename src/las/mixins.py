class DisablePreselectMixin:
    def get_search_results(self, request, queryset, search_term):
        if search_term:
            return super().get_search_results(request, queryset, search_term)
        return queryset.none(), False


class DisableModifyMixin:
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
