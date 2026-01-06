# -*- coding: utf-8 -*-
import base64
import json
import logging
from odoo import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import Flow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from google.auth.transport.requests import Request

except ImportError:
    _logger.warning("Google API libraries not installed. Please run: pip install google-api-python-client google-auth-oauthlib")
    Credentials = None
    Flow = None
    build = None
    HttpError = None
    Request = None


# --- KONFIGURASI ---
# Skop yang dibutuhkan aplikasi. Jika diubah, hapus token.json.
SCOPES = ['https://www.googleapis.com/auth/drive']
# Lokasi file client secret. Sebaiknya diatur di odoo.conf atau sebagai parameter sistem.
# Untuk sekarang, kita asumsikan admin meletakkannya di path yang bisa diakses.
# Cara terbaik adalah menyimpannya di ir.config_parameter.
CLIENT_SECRET_PARAM = 'google.drive.client.secret.json'
TOKEN_PARAM = 'google.drive.token.json'
REDIRECT_URI_PARAM = 'google.drive.redirect.uri'

def get_drive_service(env):
    """
    Menginisialisasi dan mengembalikan service object untuk Google Drive API.
    Menangani otentikasi OAuth2.
    """
    if Credentials is None:
         raise UserError(_(
            "Library Google API tidak ditemukan.\n"
            "Silakan install library berikut di server Odoo Anda:\n"
            "pip install google-api-python-client google-auth-oauthlib"
        ))

    config_params = env['ir.config_parameter'].sudo()
    
    client_secret_str = config_params.get_param(CLIENT_SECRET_PARAM)
    if not client_secret_str:
        raise UserError(_(
            "File Client Secret Google API belum diatur di Pengaturan Sistem.\n"
            "Parameter: %s"
        ) % CLIENT_SECRET_PARAM)

    try:
        client_config = json.loads(client_secret_str)
    except (json.JSONDecodeError, TypeError):
        raise UserError(_("Format Client Secret JSON tidak valid."))

    creds = None
    token_str = config_params.get_param(TOKEN_PARAM)
    if not token_str or token_str == '{}':
        # Fallback: Coba baca file token.json dari root direktori modul
        import os
        # Path relatif dari lib/gdrive_service.py ke root modul
        current_dir = os.path.dirname(os.path.abspath(__file__))
        token_path = os.path.join(current_dir, '..', 'token.json')
        
        if os.path.exists(token_path):
            try:
                with open(token_path, 'r') as f:
                    token_str = f.read()
                    _logger.info("Menggunakan token.json dari file disk: %s", token_path)
                    # Opsional: Simpan ke parameter agar next time tidak perlu baca file
                    config_params.set_param(TOKEN_PARAM, token_str)
            except Exception as e:
                _logger.warning("Gagal membaca file token.json lokal: %s", e)

    if token_str:
        try:
            token_info = json.loads(token_str)
            # DEBUG: Log keys found to identify missing ones
            _logger.info("Token Info Keys Found: %s", list(token_info.keys()))
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except (json.JSONDecodeError, TypeError):
            _logger.warning("Format token JSON tidak valid, akan coba otentikasi ulang.")
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                _logger.error("Gagal me-refresh token Google: %s", e)
                # Jika refresh gagal, kita perlu otentikasi ulang.
                # Ini bagian yang sulit di lingkungan server.
                # Opsi terbaik adalah membuat halaman controller Odoo khusus untuk otentikasi.
                raise UserError(_(
                    "Sesi Google Drive Anda telah berakhir dan gagal diperbarui secara otomatis. "
                    "Anda mungkin perlu melakukan otentikasi ulang. Hubungi tim IT untuk bantuan."
                ))
        else:
            # Skenario ini seharusnya tidak terjadi dalam penggunaan normal setelah setup awal.
            # Setup awal memerlukan proses interaktif untuk mendapatkan token pertama kali.
            # Odoo controller diperlukan untuk menangani alur redirect dari Google.
            raise UserError(_(
                "Belum ada token Google yang valid. Silakan lakukan proses otentikasi awal. "
                "Hubungi tim IT untuk mengkonfigurasi integrasi Google Drive."
            ))
            
    # Simpan token yang mungkin sudah di-refresh
    config_params.set_param(TOKEN_PARAM, creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)
        return service
    except HttpError as error:
        _logger.error("Terjadi error saat membuat service Google Drive: %s", error)
        raise UserError(_("Gagal terhubung ke Google Drive. Detail: %s") % error)


def find_folder_by_name(service, folder_name, parent_folder_id):
    """Mencari folder berdasarkan nama di dalam parent_folder_id dan mengembalikan ID-nya jika ditemukan."""
    try:
        query = f"name = '{folder_name}' and '{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        if items:
            _logger.info("Folder '%s' ditemukan dengan ID: %s", folder_name, items[0]['id'])
            return items[0]['id']
        _logger.info("Folder '%s' tidak ditemukan dalam parent folder ID: %s", folder_name, parent_folder_id)
        return None
    except HttpError as error:
        _logger.error("Gagal mencari folder '%s': %s", folder_name, error)
        return None

def create_folder(service, folder_name, parent_folder_id):
    """Membuat folder baru di dalam parent_folder_id dan mengembalikan ID-nya."""
    try:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id]
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        _logger.info("Folder '%s' berhasil dibuat dengan ID: %s", folder_name, folder.get('id'))
        return folder.get('id')
    except HttpError as error:
        _logger.error("Gagal membuat folder '%s': %s", folder_name, error)
        return None

def upload_file(service, attachment, folder_id):
    """Mengupload file dari Odoo attachment ke folder Google Drive."""
    try:
        file_metadata = {
            'name': attachment.name,
            'parents': [folder_id]
        }
        
        # ir.attachment menyimpan data dalam base64
        file_content = base64.b64decode(attachment.datas)
        
        # Perlu cara untuk mengirim konten, bukan path file.
        # Sayangnya, `google-api-python-client` tidak secara langsung mendukung upload dari memory
        # dengan cara yang simpel. Kita harus menggunakan `MediaIoBaseUpload`.
        from io import BytesIO
        from googleapiclient.http import MediaIoBaseUpload

        media = MediaIoBaseUpload(BytesIO(file_content), mimetype=attachment.mimetype, resumable=True)
        
        request = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink, thumbnailLink'
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                _logger.info("Uploaded %d%% of '%s'.", int(status.progress() * 100), attachment.name)

        _logger.info("File '%s' berhasil diupload dengan ID: %s", response.get('name'), response.get('id'))
        # Response now contains id, name, webViewLink, thumbnailLink
        return response

    except HttpError as error:
        _logger.error("Gagal mengupload file '%s': %s", attachment.name, error)
        return None
    except Exception as e:
        _logger.error("Terjadi error tidak terduga saat upload '%s': %s", attachment.name, e)
        return None

def get_folder_link(service, folder_id):
    """Mendapatkan link web untuk folder."""
    try:
        file = service.files().get(fileId=folder_id, fields='webViewLink').execute()
        return file.get('webViewLink')
    except HttpError as error:
        _logger.error("Gagal mendapatkan link untuk folder ID '%s': %s", folder_id, error)
        return None

def delete_file(service, file_id):
    """Menghapus file dari Google Drive berdasarkan ID."""
    try:
        service.files().delete(fileId=file_id).execute()
        _logger.info("File ID '%s' berhasil dihapus dari Google Drive.", file_id)
        return True
    except HttpError as error:
        _logger.error("Gagal menghapus file ID '%s': %s", file_id, error)
        return False
    except Exception as e:
        _logger.error("Error tak terduga saat menghapus file ID '%s': %s", file_id, e)
        return False
