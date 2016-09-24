from django.utils.translation import ugettext_lazy as _
from horizon import tables
from horizon import forms

class MyFilterAction(tables.FilterAction):
    name = "nova_log"
    def filter(self, table, logs, filter_string):
        """Really naive case-insensitive search."""
        # FIXME(gabriel): This should be smarter. Written for demo purposes.
        q = filter_string.lower()

        def comp(logs):
            if q in logs.name.lower():
                return True
            return False

        return filter(comp, logs)
    #     return logs

class FilterLog(tables.FilterAction):
    filter_type = "server"
    filter_choices = (("id", _("id ="), True),
                      ("time", _("time ="), True),
                      ("pid", _("pid ="), True),
                      ("level", _("level ="), True))

class LogNovaTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"))
    time = tables.Column("time", verbose_name=_("Time"))
    pid = tables.Column("pid", verbose_name=_("Pid"))
    level = tables.Column("level", verbose_name=_("Level"))

    class Meta(object):
        name = "lognovaapi"
        verbose_name = _("Log nova api")
        table_actions = (MyFilterAction,)