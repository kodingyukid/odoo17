# trainer_schedule/__manifest__.py
{
    'name': 'Jadwal Trainer (Trainer Schedule)',
    'version': '1.0',
    'summary': 'Modul untuk mengelola jadwal pertemuan trainer dengan siswa.',
    'description': """
        Modul ini menyediakan fitur untuk:
        - Mengelola data siswa
        - Mencatat jadwal pertemuan
        - Melihat jadwal dalam bentuk kalender dan pivot (grid)
    """,
    'author': 'Nama Anda',
    'category': 'Education',
    'depends': ['base', 'calendar'],  # Bergantung pada modul base dan calendar
    'data': [
        'security/ir.model.access.csv',
        'reports/reports.xml',
        'reports/trainer_schedule_report.xml',
        'views/trainer_schedule_wizard_views.xml',
        'views/trainer_schedule_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
