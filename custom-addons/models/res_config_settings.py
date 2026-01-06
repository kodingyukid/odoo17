# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_base_url = fields.Char(
        string='WAHA Base URL',
        config_parameter='whatsapp.base_url',
        help="URL dasar dari WAHA API, contoh: http://localhost:3000"
    )
    whatsapp_api_key = fields.Char(
        string='WAHA API Key',
        config_parameter='whatsapp.api_key',
        help="API Key untuk otentikasi dengan WAHA API."
    )
