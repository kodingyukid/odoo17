{
    'name': 'Staff Daily Journal',
    'version': '1.3',
    'category': 'Human Resources',
    'summary': 'Catat jurnal harian staff atau Internship',
    'description': 'Modul untuk mencatat jurnal harian staff.',
    'author': 'KodingYuk',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/staff_journal_views.xml',
        'data/mscustomer_sequence.xml',
        'data/msnipl_sequence.xml',
        'data/msorder_sequence.xml',
        'data/msrole_sequence.xml',
    ],

    'installable': True,
    'application': True,
}
