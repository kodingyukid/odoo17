# -*- coding: utf-8 -*-
{
    'name': "WhatsApp Connector",
    'summary': "Kirim pesan WhatsApp melalui Waha (WAHA) API.",
    'description': """
        Modul ini menyediakan fungsionalitas untuk mengirim pesan WhatsApp
        langsung dari Odoo menggunakan WAHA (WhatsApp HTTP API).
        Konfigurasi API Key dan Base URL dapat diatur melalui menu Pengaturan.
    """,
    'author': "Gemini",
    'website': "https://www.google.com",
    'category': 'Tools',
    'version': '17.0.1.0.0',
    'depends': ['base', 'base_setup'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/whatsapp_send_wizard_view.xml',
        'views/res_config_settings_views.xml',
        'views/menu.xml',
    ],
    'external_dependencies': {
        'python': ['requests'],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
