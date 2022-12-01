from jwcm.core.models import Person
from jwcm.lpw.models import PersonAvailability


def batch_read_and_create_person(df_batch, congregation):
    list_person = []
    true_options = 'sim', 's'
    anciao_options = 'anciao', 'ancião', 'a'
    sm_oprtions = 'servo ministerial', 'sm'
    pe_options = 'pioneiro especial', 'pe'
    pr_options = 'pioneiro regular', 'pr'
    pa_options = 'pioneiro auxiliar', 'pa'

    for index, row in df_batch.iterrows():
        full_name = row[0]
        telephone = row[1]

        if row[2].lower() in ('masculino', 'm'):
            gender = Person.MASCULINO
        else:
            gender = Person.FEMININO

        if row[3].lower() in anciao_options:
            privilege = Person.ANCIAO
        elif row[3].lower() in sm_oprtions:
            privilege = Person.SERVO_MINISTERIAL
        else:
            privilege = Person.SEM_PRIVILEGIO_ESPECIAL

        if row[4].lower() in pe_options:
            modality = Person.PIONEIRO_ESPECIAL
        elif row[4].lower() in pr_options:
            modality = Person.PIONEIRO_REGULAR
        elif row[4].lower() in pa_options:
            modality = Person.PIONEIRO_AUXILIAR
        else:
            modality = Person.PUBLICADOR

        #leitor de A Sentinela
        if row[5].lower() in true_options:
            watchtower_reader = True
        else:
            watchtower_reader = False

        # leitor de Estudo Bíblico
        if row[6].lower() in true_options:
            bible_study_reader = True
        else:
            bible_study_reader = False

        # indicador
        if row[7].lower() in true_options:
            indicator = True
        else:
            indicator = False

        # mic
        if row[8].lower() in true_options:
            mic = True
        else:
            mic = False

        # notebook/mesa de som
        if row[9].lower() in true_options:
            note_sound_table = True
        else:
            note_sound_table = False

        # indicador zoom
        if row[10].lower() in true_options:
            zoom_indicator = True
        else:
            zoom_indicator = False

        # partes de estudante
        if row[11].lower() in true_options:
            student_parts = True
        else:
            student_parts = False

        # presidente da reunião de fim de semana
        if row[12].lower() in true_options:
            weekend_meeting_president = True
        else:
            weekend_meeting_president = False

        # presidente da reunião de meio de semana
        if row[13].lower() in true_options:
            midweek_meeting_president = True
        else:
            midweek_meeting_president = False

        person = Person(full_name=full_name, telephone=telephone, gender=gender, privilege=privilege, modality=modality,
                        watchtower_reader=watchtower_reader, bible_study_reader=bible_study_reader,
                        indicator=indicator, mic=mic, note_sound_table=note_sound_table, zoom_indicator=zoom_indicator,
                        weekend_meeting_president=weekend_meeting_president, midweek_meeting_president=midweek_meeting_president,
                        student_parts=student_parts,
                        congregation=congregation)


        list_person.append(person)

    Person.objects.bulk_create(list_person)

    for person in list_person:
        # após salvar o objeto no banco, crio o objeto relacionado à ele para cada dia da semana
        for weekday in range(0, 7):
            person_availability = PersonAvailability.objects.create(weekday=weekday, morning=False, afternoon=False, night=False)
            person_availability.person.add(person)
