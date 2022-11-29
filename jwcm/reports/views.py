import io
from django.views.generic import FormView
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate
from reportlab.lib.styles import getSampleStyleSheet
from jwcm.reports.forms import ReportsForm
from jwcm.reports.reports import Report



styles = getSampleStyleSheet()


class ReportsView(FormView):
    template_name = 'reports.html'
    form_class = ReportsForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['button_mechanical_privileges'] = 'Privilégios mecânicos'
        context['button_student_parts'] = 'Partes de estudante'
        context['button_midweek_meeting'] = 'Reunião de meio de semana'
        context['button_weekend_meeting'] = 'Reunião de fim de semana'
        context['title'] = 'Relatórios'
        return context


    def post(self, request, *args, **kwargs):
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        buffer = io.BytesIO()
        simple_doc = SimpleDocTemplate(buffer, pagesize=letter, bottomup=0)
        reports = Report(start_date, end_date, self.request.user.profile.congregation, simple_doc, buffer)

        if 'mechanical_privileges' in request.POST:
            reports.mechanical_privileges_report()
        elif 'student_parts' in request.POST:
            reports.student_parts_report()
        elif 'midweek_meeting' in request.POST:
            reports.midweek_meeting_report()
        else:
            reports.weekend_meeting_report()

        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename=reports.report_filename)