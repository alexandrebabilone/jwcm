from django.shortcuts import render
import datetime

def _verify_parts():
    current_date = datetime.date.today()
    num_year, num_week, num_day = current_date.isocalendar()