from django.db import models
#como importar os choices se nao posso importar a classe Person?


class PartQuerySet(models.QuerySet):
    def sorted_by_date_desc(self):
        return self.order_by('-date')

    def part_dates(self):
        return self.values('date').distinct().order_by('-date')
