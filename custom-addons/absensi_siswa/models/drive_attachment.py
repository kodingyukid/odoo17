# -*- coding: utf-8 -*-
from odoo import models, fields, api

from odoo import models, fields, api
from ..lib import gdrive_service

class AbsensiDriveAttachment(models.Model):
    _name = 'absensi.drive.attachment'
    _description = 'Attachment File Google Drive'
    
    def unlink(self):
        # Hapus file dari Google Drive sebelum menghapus record Odoo
        try:
            service = gdrive_service.get_drive_service(self.env)
            for rec in self:
                if rec.file_id:
                    gdrive_service.delete_file(service, rec.file_id)
        except Exception as e:
            # Jangan biarkan error drive mencegah penghapusan record Odoo
            # Cukup log saja atau beri warning non-blocking
            pass
            
        return super(AbsensiDriveAttachment, self).unlink()

    name = fields.Char(string='Nama File', required=True)
    file_id = fields.Char(string='File ID Google', required=True)
    url = fields.Char(string='Link Preview', help="Link untuk melihat file di browser")
    thumbnail_url = fields.Char(string='Thumbnail', help="Link thumbnail dari Google Drive")
    
    absensi_line_id = fields.Many2one(
        'absensi.siswa.absensi.line', 
        string='Baris Absensi',
        ondelete='cascade',
        index=True
    )
    
    def action_open_link(self):
        self.ensure_one()
        if self.url:
            return {
                'type': 'ir.actions.act_url',
                'url': self.url,
                'target': 'new',
            }
