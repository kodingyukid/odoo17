# -*- coding: utf-8 -*-
{
    'name': "Absensi Siswa",
    'summary': "Modul untuk mengelola absensi pertemuan siswa.",
    'description': """
        Modul ini mengelola data Siswa (dari Customer), 
        Trainer (dari Employee), dan mencatat absensi per pertemuan.
    """,
    'author': "Gemini",
    'website': "-",
    'category': 'Uncategorized',
    'version': '1.0',
    
    # TAMBAHKAN 'hr' DI SINI
    'depends': ['base', 'mail', 'hr', 'account', 'students', 'modul_pembelajaran'], 
    
    'data': [
        'security/ir.model.access.csv',
        'data/google_drive_config.xml',
        'views/menu.xml',
        'views/siswa_view.xml',
        'views/trainer_view.xml',
        'views/absensi_view.xml',
        'views/enrollment_views_extension.xml',
        'views/upload_wizard_view.xml',
        'views/drive_attachment_view.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}