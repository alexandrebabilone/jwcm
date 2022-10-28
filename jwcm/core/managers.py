from django.db import models
#como importar os choices se nao posso importar a classe Person?


class CongregationQuerySet(models.QuerySet):
    def select_host_congregations(self):
        return self.filter(host=True)


class MeetingQuerySet(models.QuerySet):
    def select_range_per_congregation(self, start_date, end_date, congregation):
        return self.filter(congregation=congregation).filter(date__gte=start_date).filter(date__lte=end_date).order_by('date')

    def weekend_meetings_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(type=1).order_by('date')

    def meetings_per_congregation_asc(self, congregation):
        return self.filter(congregation=congregation).order_by('date')

    def midweek_meetings_per_congregation_desc(self, congregation):
        return self.filter(congregation=congregation).filter(type=0).order_by('-date')

    def select_range_weekend_meetings_per_congregation(self, congregation, start_date, end_date):
        return self.filter(congregation=congregation).filter(date__gte=start_date).filter(date__lte=end_date).order_by('date')

class PersonQuerySet(models.QuerySet):
    def elders_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(privilege=0)

    def ministerial_servants_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(privilege=1)

    def elders_and_ministerial_servants_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(models.Q(privilege=0) | models.Q(privilege=1))

    def watchtower_readers_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(watchtower_reader=True)

    def bible_study_readers_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(bible_study_reader=True)

    def indicators_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(indicator=True)

    def mics_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(mic=True)

    def note_sound_tables_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(note_sound_table=True)

    def zoom_indicators_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(zoom_indicator=True)

    def weekend_meeting_presidents_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(weekend_meeting_president=True)

    def midweek_meeting_presidents_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(midweek_meeting_president=True)

    def student_parts_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(student_parts=True).filter(privilege=2)

    def men_student_parts_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(gender=0).filter(student_parts=True).filter(privilege=2)


#PeriodManager = models.Manager.from_queryset(PeriodQuerySet)