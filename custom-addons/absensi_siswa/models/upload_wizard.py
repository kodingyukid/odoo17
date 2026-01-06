# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

# Placeholder untuk fungsi-fungsi Google Drive
# Anda perlu menginstal library Google:
# pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
try:
    from ..lib import gdrive_service
except ImportError:
    gdrive_service = None

class UploadWizard(models.TransientModel):
    _name = 'upload.wizard'
    _description = 'Wizard untuk Upload File ke Google Drive'

    absensi_line_id = fields.Many2one('absensi.siswa.absensi.line', string='Baris Absensi', readonly=True)
    
    attachment_ids = fields.Many2many(
        'ir.attachment', 
        string='File untuk Diupload (Maks 5)',
        required=True
    )

    def action_confirm_upload(self):
        self.ensure_one()
        
        if len(self.attachment_ids) > 5:
            raise UserError(_("Anda tidak bisa mengupload lebih dari 5 file."))

        if not gdrive_service:
            raise UserError(_(
                "Library Google Drive tidak ditemukan. Silakan hubungi tim IT "
                "untuk menginstal library yang dibutuhkan:\n"
                "pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            ))

        line = self.absensi_line_id
        siswa = line.absensi_id.siswa_id

        # Struktur folder: ID Siswa-Nama Siswa / Tanggal Pertemuan
        student_folder_name = f"{siswa.id}-{siswa.name}"
        attendance_folder_name = line.tanggal_waktu.strftime('%Y-%m-%d')
        
        try:
            # 1. Dapatkan service Google Drive
            service = gdrive_service.get_drive_service(self.env)
            
            # 2. Dapatkan ID folder utama dari parameter sistem
            main_folder_id = self.env['ir.config_parameter'].sudo().get_param('google.drive.main.folder.id')
            if not main_folder_id:
                raise UserError(_("ID Folder utama Google Drive belum diatur di Pengaturan. Hubungi tim IT."))
            
            # 3. Cari atau Buat folder siswa
            student_folder_id = gdrive_service.find_folder_by_name(service, student_folder_name, main_folder_id)
            if not student_folder_id:
                student_folder_id = gdrive_service.create_folder(service, student_folder_name, main_folder_id)
            
            if not student_folder_id:
                raise UserError(_("Gagal membuat atau menemukan folder untuk siswa di Google Drive."))

            # 4. Cari atau Buat subfolder tanggal di dalam folder siswa
            folder_id = gdrive_service.find_folder_by_name(service, attendance_folder_name, student_folder_id)
            if not folder_id:
                folder_id = gdrive_service.create_folder(service, attendance_folder_name, student_folder_id)

            if not folder_id:
                raise UserError(_("Gagal membuat atau menemukan folder tanggal absensi di Google Drive. Periksa log untuk detailnya."))

            # 5. Upload file-file
            file_metadata_list = []
            for attachment in self.attachment_ids:
                file_metadata = gdrive_service.upload_file(service, attachment, folder_id)
                if file_metadata:
                    file_metadata_list.append(file_metadata)
                    
                    # Simpan detail file ke model database kita
                    # Gunakan sudo() untuk memastikan record bisa dibuat meski user memiliki hak akses terbatas
                    self.env['absensi.drive.attachment'].sudo().create({
                        'name': file_metadata.get('name'),
                        'file_id': file_metadata.get('id'),
                        'url': file_metadata.get('webViewLink'),
                        'thumbnail_url': file_metadata.get('thumbnailLink'),
                        'absensi_line_id': line.id,
                    })
            
            if len(file_metadata_list) != len(self.attachment_ids):
                 # Ini hanya notifikasi, mungkin beberapa file berhasil, beberapa gagal.
                 # Untuk kesederhanaan, kita anggap semua harus berhasil.
                raise UserError(_("Beberapa file gagal diupload. Silakan coba lagi atau hubungi tim IT."))

            # 6. Dapatkan link folder dan simpan
            folder_url = gdrive_service.get_folder_link(service, folder_id)
            if folder_url:
                line.google_drive_folder_url = folder_url
            
            # Beri notifikasi sukses
            # Beri notifikasi sukses dan reload halaman
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',  # Ini akan mereload view di belakang wizard, dan biasanya menutup wizard
            }

        except Exception as e:
            # Jika ada error apapun, tampilkan pesan ke user
            raise UserError(_("Terjadi kesalahan saat mengupload ke Google Drive: %s\n\nJika masalah berlanjut, hubungi tim IT.") % str(e))

        return {'type': 'ir.actions.act_close_wizard_and_reload_view'}

class IrActionsActCloseWizardAndReloadView(models.AbstractModel):
    _name = 'ir.actions.act_close_wizard_and_reload_view'
    _description = 'Close wizard and reload view'

    @api.model
    def execute(self):
        return {'type': 'ir.actions.act_close_wizard_and_reload_view'}