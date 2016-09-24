from django.utils.translation import ugettext_lazy as _
from horizon import tables

# class StatusFilter(tables.FilterAction):
#     param_name = "q"
#     filter_type = "filter"

class FilterLog(tables.FilterAction):
    name = "dong_novalog_filter"
    verbose_name = "filter_server"
    filter_type = "server"
    filter_choices = (("id", _("id ="), True),
                      ("time", _("time ="), False),
                      ("pid", _("process id ="), True),
                      ("level", _("level ="), False))

class LogNovaTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"))
    time = tables.Column("time", verbose_name=_("Time"))
    pid = tables.Column("pid", verbose_name=_("Pid"))
    level = tables.Column("level", verbose_name=_("Level"))

    class Meta(object):
        name = "lognovaapi"
        verbose_name = _("Log nova api")
        table_actions = (FilterLog,)