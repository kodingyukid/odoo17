# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
import requests
import logging

_logger = logging.getLogger(__name__)

class WhatsappSendWizard(models.TransientModel):
    _name = 'whatsapp.send.wizard'
    _description = 'Wizard untuk Kirim Pesan WhatsApp'

    phone_number = fields.Char(string="Nomor Telepon", required=True, help="Nomor telepon penerima dengan kode negara, contoh: 6281234567890")
    message = fields.Text(string="Pesan", required=True)

    def action_send_message(self):
        self.ensure_one()
        
        # Mengambil konfigurasi dari system parameters
        get_param = self.env['ir.config_parameter'].sudo().get_param
        base_url = get_param('whatsapp.base_url')
        api_key = get_param('whatsapp.api_key')

        if not base_url or not api_key:
            raise UserError(_("Konfigurasi WAHA (Base URL atau API Key) belum diatur. Silakan atur di menu Pengaturan > Umum > WhatsApp."))

        # Membersihkan nomor telepon dari karakter yang tidak perlu
        clean_phone = ''.join(filter(str.isdigit, self.phone_number))

        # Endpoint untuk mengirim pesan teks
        api_url = f"{base_url.rstrip('/')}/api/sessions/default/chats/{clean_phone}@c.us/messages"
        
        headers = {
            'Content-Type': 'application/json',
            'X-Api-Key': api_key,
        }
        
        payload = {
            'body': self.message,
        }

        try:
            _logger.info(f"Mengirim pesan ke {api_url} dengan payload: {payload}")
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status() # Menghasilkan error jika status code bukan 2xx

            _logger.info(f"Respon dari WAHA API: {response.status_code} - {response.text}")
            
            # Tampilkan notifikasi sukses
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Sukses'),
                    'message': _('Pesan WhatsApp berhasil dikirim.'),
                    'type': 'success',
                    'sticky': False,
                }
            }

        except requests.exceptions.Timeout:
            _logger.error("Timeout saat menghubungi WAHA API.")
            raise UserError(_("Waktu koneksi ke WAHA API habis. Pastikan server dapat dijangkau dan coba lagi."))
        except requests.exceptions.HTTPError as err:
            _logger.error(f"HTTP Error dari WAHA API: {err.response.status_code} - {err.response.text}")
            raise UserError(_("Gagal mengirim pesan. WAHA API memberikan respon error: %s - %s") % (err.response.status_code, err.response.text))
        except requests.exceptions.RequestException as e:
            _logger.error(f"Error saat mengirim permintaan ke WAHA API: {e}")
            raise UserError(_("Terjadi kesalahan saat mencoba terhubung ke WAHA API. Pastikan Base URL benar dan server WAHA sedang berjalan. Error: %s") % e)

        return {'type': 'ir.actions.act_window_close'}
