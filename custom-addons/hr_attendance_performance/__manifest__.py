{
    'name': 'HR Attendance Performance',
    'version': '1.1',
    'category': 'Human Resources',
    'summary': 'Analyze Employee Attendance Performance',
    'description': """
        Calculate employee performance based on attendance records.
        Features:
        - Monthly Total Hours
        - Weekly Average Hours
        - Performance Status based on configurable rules
    """,
    'author': 'Gemini Agent',
    'depends': ['hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/performance_views.xml',
        'reports/performance_report.xml',
    ],
    'installable': True,
    'application': False,
}
