from django.contrib.admin import SimpleListFilter


class SoftDeleteFilter(SimpleListFilter):
    title = "Status"
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return (
            ("alive", "Alive"),
            ("deleted", "Deleted"),
        )

    def queryset(self, request, queryset):
        if self.value() == "deleted":
            return queryset.filter(is_deleted=True)

        return queryset.filter(is_deleted=False)