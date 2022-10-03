from jwcm.core.models import Meeting
from jwcm.life_and_ministry.models import Part
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus.tables import Table
from reportlab.platypus import TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet


styles = getSampleStyleSheet()

class Report:
    def __init__(self, start_date, end_date, congregation, simple_doc):
        self.report_filename = ''
        self.congregation = congregation
        self.simple_doc = simple_doc
        self.start_date = start_date
        self.end_date = end_date
        self.set_meetings()

    def set_meetings(self):
        self.meetings = Meeting.objects.select_range_per_congregation(self.start_date, self.end_date, self.congregation)

############################# mechanical_privileges_report #############################
    def mechanical_privileges_report(self):
        table_data = self.make_table_data_mechanical_privileges(self.meetings)
        self.make_table_report(table_data, 'Privilégios mecânicos')
        self.report_filename = f'mechanical_privileges_{self.start_date}_to_{self.end_date}.pdf'

    def make_table_data_mechanical_privileges(self, meetings):
        table_data = []
        table_data.append(['Data', 'Indicadores', 'Microfones', 'Áudio e vídeo'])

        for meeting in meetings:
            mic_1, mic_2, indicator_1, indicator_2, note, zoom_indicator = '', '', '', '', '', ''

            if meeting.indicator_1:
                indicator_1 = meeting.indicator_1.full_name

            if meeting.indicator_2:
                indicator_2 = meeting.indicator_2.full_name

            if meeting.mic_1:
                mic_1 = meeting.mic_1.full_name

            if meeting.mic_2:
                mic_2 = meeting.mic_2.full_name

            if meeting.note_sound_table:
                note = meeting.note_sound_table.full_name

            if meeting.zoom_indicator:
                zoom_indicator = meeting.zoom_indicator.full_name

            table_data.append([meeting.date.strftime("%d/%m/%Y"), f'{indicator_1} e {indicator_2}',
                               f'{mic_1} e {mic_2}',
                               f'{note} e {zoom_indicator}'])

        return table_data

    def make_table_report(self, table_data, title):
        report_elements = []
        self.simple_doc.title = title
        table = Table(table_data)
        table.setStyle(self.table_style_mechanical_privileges())
        report_elements.append(Paragraph(title, styles['Title']))
        report_elements.append(Spacer(1 * cm, 1 * cm))
        report_elements.append(table)
        self.simple_doc.build(report_elements)

    def table_style_mechanical_privileges(self):
        return TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])
############################# mechanical_privileges_report #############################

############################# midweek_meeting_report #############################
    def midweek_meeting_report(self):
        self.make_data_midweek_meeting_report()
        self.report_filename = f'midweek_meeting_{self.start_date}_to_{self.end_date}.pdf'

    def make_data_midweek_meeting_report(self):
        report_elements = []

        self.simple_doc.title = 'Programação da reunião de meio de semana'
        report_elements.append(Paragraph(self.simple_doc.title, styles['Title']))
        report_elements.append(Spacer(1 * cm, 1 * cm))

        for meeting in self.meetings:
            table_data, section_lines = [], []
            index = 0

            if meeting.is_weekend_meeting():
                continue

            table_data.append([f'{meeting.week if meeting.week else meeting.date.strftime("%d/%m/%Y")} '
                               f'| {meeting.weekly_reading if meeting.weekly_reading else "Leitura semanal da Bíblia"}',
                               f'Presidente: {meeting.president}'])

            if meeting.initial_song:
                table_data.append([meeting.initial_song, ''])

            index += 1
            section_lines.append(index)

            assignments_tesouros = meeting.lifeandministryassignment_set.filter(part__section=Part.TESOUROS_DA_PALAVRA_DE_DEUS)
            assignments_ministerio = meeting.lifeandministryassignment_set.filter(part__section=Part.FACA_SEU_MELHOR_NO_MINISTÉRIO)
            assignments_vida = meeting.lifeandministryassignment_set.filter(part__section=Part.NOSSA_VIDA_CRISTA)

            table_data.append(['TESOUROS DA PALAVRA DE DEUS', ''])
            self._populate_table(assignments_tesouros, table_data)
            index += len(assignments_tesouros) + 1
            section_lines.append(index)

            table_data.append(['FAÇA SEU MELHOR NO MINISTÉRIO', ''])
            self._populate_table(assignments_ministerio, table_data)
            index += len(assignments_ministerio) + 1
            section_lines.append(index)

            table_data.append(['NOSSA VIDA CRISTÃ', ''])
            if meeting.middle_song:
                table_data.append([meeting.middle_song, ''])
            self._populate_table(assignments_vida, table_data)
            index += len(assignments_vida) + 2

            if meeting.final_song:
                table_data.append([meeting.final_song, ''])

            table = Table(table_data, colWidths=(160 * mm, 40 * mm))
            table.setStyle(self.table_style_midweek_meeting(section_lines))
            report_elements.append(table)
            report_elements.append(PageBreak())

        self.simple_doc.build(report_elements)


    def _populate_table(self, assignments, table_data):
        people = ''

        for assignment in assignments:
            if assignment.owner:
                people = assignment.owner.full_name

            if assignment.assistant:
                people += '/' + assignment.assistant.full_name

            p = Paragraph(assignment.part.theme, styles["BodyText"])
            table_data.append([p, people])

    def table_style_midweek_meeting(self, list_line_section):
        list_styles = []
        section_colors = [colors.gray, colors.darkgoldenrod, colors.darkred]

        list_styles.append(('ALIGN', (0, 0), (0, -1), 'LEFT'))
        list_styles.append(('ALIGN', (1, 0), (1, -1), 'RIGHT'))
        list_styles.append(('VALIGN', (1, 0), (1, -1), 'TOP'))
        list_styles.append(('FONTSIZE', (0, 0), (-1, -1), 10))
        list_styles.append(('BOTTOMPADDING', (0, 0), (-1, 0), 10))

        for index, section_color in zip(list_line_section, section_colors):
            list_styles.append(('TEXTCOLOR', (0, index), (0, index), colors.white))
            list_styles.append(('BACKGROUND', (0, index), (0, index), section_color))
            list_styles.append(('FONTNAME', (0, index), (0, index), 'Courier-Bold'))

        return TableStyle(list_styles)
############################# midweek_meeting_report #############################

############################# weekend_meeting_report #############################
    def weekend_meeting_report(self):
        table_data = self.make_table_data_weekend_meeting_report()
        self.make_table_report(table_data, 'Reunião de fim de semana')
        self.report_filename = f'weekend_meeting__{self.start_date}_to_{self.end_date}.pdf'

    def make_table_data_weekend_meeting_report(self):
        table_data = []
        table_data.append(['Data', 'Orador', 'Discurso', 'Leitor de A Sentinela'])

        for meeting in self.meetings:
            speaker_name, speech_theme, watchtower_reader = '', '', ''

            if meeting.public_assignment:
                if meeting.public_assignment.speaker:
                    speaker_name = meeting.public_assignment.speaker.full_name

                if meeting.public_assignment.speech:
                    speech_theme = meeting.public_assignment.speech.theme

                if meeting.watchtower_reader:
                    watchtower_reader = meeting.watchtower_reader.full_name

            table_data.append([meeting.date.strftime("%d/%m/%Y"),
                               f'{speaker_name}',
                               f'{speech_theme}',
                               f'{watchtower_reader}'])

        return table_data
############################# weekend_meeting_report #############################

############################# student_part_report #############################

    def student_parts_report(self):
        #make_data_students_parts_report(simple_doc, meetings, 'DESIGNAÇÃO PARA A REUNIÃO NOSSA VIDA E MINISTERIO CRISTÃO')
        self.report_filename = f'student_parts_{self.start_date}_to_{self.end_date}.pdf'


    def make_data_students_parts_report(self, simple_doc, meetings, title):
        report_elements = []

        simple_doc.title = title
        report_elements.append(Paragraph(title, styles['Title']))
        report_elements.append(Spacer(1 * cm, 1 * cm))

        for meeting in meetings:
            table_data, part_themes = [], []

            if meeting.is_weekend_meeting():
                continue

            assignments_tesouros = meeting.lifeandministryassignment_set.filter(
                part__section=Part.TESOUROS_DA_PALAVRA_DE_DEUS)
            assignments_ministerio = meeting.lifeandministryassignment_set.filter(
                part__section=Part.FACA_SEU_MELHOR_NO_MINISTÉRIO)

            for student_part in assignments_tesouros:
                if 'Leitura da Bíblia: (4 min)' in student_part.part.theme:
                    part_themes.append(student_part.part.theme)

            for student_part in assignments_ministerio:
                part_themes.append(student_part.part.theme)

            for theme in part_themes:
                table_data.append([f'Data: {meeting.week}'])
                table_data.append([f'Designação: {theme}'])
                table_data.append([f''])
                table_data.append([f'Observação para o estudante: A lição da brochura Melhore e a fonte de materia para a sua designação estão na Apostila da Reuniao Vida e Ministerio. '
                                   'Estude a lição da brochura para saber como aplicar o ponto que voce vai considerar.'])


            table = Table(table_data, colWidths=(160 * mm))
            report_elements.append(table)
            report_elements.append(PageBreak())

        simple_doc.build(report_elements)


    def _populate_student_pars(self, assignments, table_data):
        owner, assistant = '', ''

        for assignment in assignments:
            if assignment.owner:
                owner = assignment.owner.full_name

            table_data.append(f'Nome: {owner}')

            if assignment.assistant:
                assistant = assignment.assistant.full_name

            table_data.append(f'Ajudante: {assistant}')

            p = Paragraph(assignment.part.theme, styles["BodyText"])
            table_data.append([p, 'people'])
############################# student_part_report #############################