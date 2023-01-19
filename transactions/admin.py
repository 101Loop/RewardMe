from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import RewardPoints, Transaction

admin.site.register(RewardPoints, SimpleHistoryAdmin)
admin.site.register(Transaction, SimpleHistoryAdmin)
