from django.db import models



class DayLPWQuerySet(models.QuerySet):
    def select_per_congregation_and_month(self, congregation, begin_date, end_date):
        return self.filter(congregation=congregation).filter(date__gte=begin_date).filter(date__lte=end_date).order_by('date')
