# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    whatsapp_base_url = fields.Char(
        string="WAHA Base URL",
        config_parameter="whatsapp.base_url",
        help="URL dasar dari WAHA API, contoh: http://localhost:3000"
    )

    whatsapp_api_key = fields.Char(
        string="WAHA API Key",
        config_parameter="whatsapp.api_key",
        help="API Key untuk otentikasi dengan WAHA API."
    )

    def action_test_connection(self):
        if not self.whatsapp_base_url or not self.whatsapp_api_key:
            raise UserError(_(
                "Konfigurasi WhatsApp belum lengkap.\n"
                "Silakan isi Base URL dan API Key terlebih dahulu."
            ))

        api_url = f"{self.whatsapp_base_url.rstrip('/')}/api/sessions"
        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": self.whatsapp_api_key,
        }

        _logger.info("WAHA Test URL: %s", api_url)

        try:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=10
            )

            _logger.info(
                "WAHA Test RESPONSE: %s - %s",
                response.status_code,
                response.text
            )

            if response.status_code == 200:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('Koneksi Berhasil'),
                        'message': _('Koneksi ke WAHA API berhasil.'),
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(_(
                    "Gagal terhubung ke WAHA API.\n"
                    "Status: %s\n"
                    "Respon: %s"
                ) % (response.status_code, response.text))

        except requests.exceptions.Timeout:
            _logger.exception("Timeout saat tes koneksi WAHA")
            raise UserError(_("Timeout saat menghubungi WAHA API."))

        except requests.exceptions.RequestException as e:
            _logger.exception("Error saat tes koneksi WAHA")
            raise UserError(_("Koneksi ke WAHA gagal: %s") % e)
