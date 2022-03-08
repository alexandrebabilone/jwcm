from django.forms import DateInput, TimeInput, DateTimeInput

class DatePickerInput(DateInput):
    input_type = 'date'

class TimePickerInput(TimeInput):
    input_type = 'time'

class DateTimePickerInput(DateTimeInput):
    input_type = 'datetime'
