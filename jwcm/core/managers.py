from django.db import models
#como importar os choices se nao posso importar a classe Person?



class PersonQuerySet(models.QuerySet):
    def elders_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(privilege=0)

    def ministerial_servants_per_congregation(self, congregation):
        return self.filter(congregation=congregation).filter(privilege=1)

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
        return self.filter(congregation=congregation).filter(student_parts=True)


#PeriodManager = models.Manager.from_queryset(PeriodQuerySet)