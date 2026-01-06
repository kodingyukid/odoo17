# -*- coding: utf-8 -*-

from odoo import models, fields, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)


class WhatsappSendWizard(models.TransientModel):
    _name = 'whatsapp.send.wizard'
    _description = 'Wizard Kirim WhatsApp via WAHA'

    phone_number = fields.Char(
        string="Nomor Telepon",
        required=True,
        help="Contoh: 6281234567890"
    )
    message = fields.Text(string="Pesan", required=True)

    def action_send_message(self):
        self.ensure_one()

        # =========================
        # Ambil konfigurasi WAHA
        # =========================
        get_param = self.env['ir.config_parameter'].sudo().get_param
        base_url = get_param('whatsapp.base_url')
        api_key = get_param('whatsapp.api_key')

        if not base_url or not api_key:
            raise UserError(_(
                "Konfigurasi WhatsApp belum lengkap.\n"
                "Silakan isi Base URL dan API Key."
            ))

        # =========================
        # Normalisasi nomor
        # =========================
        clean_phone = ''.join(filter(str.isdigit, self.phone_number))
        if not clean_phone.startswith('62'):
            raise UserError(_("Nomor WA harus diawali 62"))

        chat_id = f"{clean_phone}@c.us"

        # =========================
        # ENDPOINT SESUAI DOKUMENTASI
        # =========================
        api_url = f"{base_url.rstrip('/')}/api/sendText"

        headers = {
            "Content-Type": "application/json",
            "X-Api-Key": api_key,
        }

        payload = {
            "session": "default",
            "chatId": chat_id,
            "text": self.message,
        }

        _logger.info("WAHA URL: %s", api_url)
        _logger.info("WAHA PAYLOAD: %s", payload)

        try:
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=15
            )

            _logger.info(
                "WAHA RESPONSE: %s - %s",
                response.status_code,
                response.text
            )

            if response.status_code not in (200, 201):
                raise UserError(_(
                    "Gagal mengirim pesan WhatsApp.\n"
                    "Status: %s\n"
                    "Respon: %s"
                ) % (response.status_code, response.text))

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Berhasil'),
                    'message': _('Pesan WhatsApp berhasil dikirim.'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except requests.exceptions.Timeout:
            _logger.exception("Timeout WAHA")
            raise UserError(_("Timeout saat menghubungi WAHA API"))

        except requests.exceptions.RequestException as e:
            _logger.exception("Error WAHA")
            raise UserError(_("Koneksi ke WAHA gagal: %s") % e)
