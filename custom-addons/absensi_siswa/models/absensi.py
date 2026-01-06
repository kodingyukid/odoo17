# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class AbsensiSiswa(models.Model):
    _name = 'absensi.siswa.absensi'
    _description = 'Absensi Siswa'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Judul Absensi', compute='_compute_name', store=True)
    
    enrollment_id = fields.Many2one(
        'siswa.kursus.enrollment',
        string='Pendaftaran Kursus',
        required=True,
        ondelete='cascade',
        index=True
    )
    
    # Related field for easy access/display
    siswa_id = fields.Many2one(
        'm.siswa', 
        string='Siswa', 
        related='enrollment_id.siswa_id',
        store=True,
        readonly=True
    )
    
    # Related field for the domain in the view
    modul_id = fields.Many2one(
        'modul.pembelajaran',
        related='enrollment_id.modul_id',
        string='Modul Pembelajaran',
        store=True,
        readonly=True
    )
    
    attendance_line_ids = fields.One2many(
        'absensi.siswa.absensi.line', 
        'absensi_id', 
        string='Detail Pertemuan'
    )

    pertemuan_count = fields.Integer(string='Jumlah Pertemuan', compute='_compute_pertemuan_count', store=True)

    @api.depends('attendance_line_ids')
    def _compute_pertemuan_count(self):
        for rec in self:
            rec.pertemuan_count = len(rec.attendance_line_ids)
    
    @api.depends('enrollment_id.name')
    def _compute_name(self):
        for rec in self:
            if rec.enrollment_id:
                rec.name = f"Absensi untuk {rec.enrollment_id.name}"
            else:
                rec.name = "Absensi Baru"

    _sql_constraints = [
        ('enrollment_id_uniq', 'unique(enrollment_id)', 'Setiap pendaftaran kursus hanya boleh punya satu lembar absensi!')
    ]


class AbsensiSiswaLine(models.Model):
    _name = 'absensi.siswa.absensi.line'
    _description = 'Baris Absensi Siswa'
    _order = 'sequence, pertemuan_ke'
    _rec_name = 'display_name'

    absensi_id = fields.Many2one('absensi.siswa.absensi', string='Absensi', ondelete='cascade')
    pertemuan_ke = fields.Integer(string='Pertemuan Ke') # Removed readonly=True
    sequence = fields.Integer(string='Urutan', default=10) # Added sequence field
    
    status = fields.Selection([
        ('hadir', 'Hadir'),
        ('izin', 'Izin'),
        ('absen', 'Absen/Tidak Hadir')
    ], string='Status Kehadiran', tracking=True)
    
    # --- PERUBAHAN DI SINI ---
    # Model diubah dari 'absensi.siswa.trainer' menjadi 'hr.employee'
    trainer_id = fields.Many2one(
        'hr.employee', 
        string='Trainer (Employee)'
    )
    # -------------------------
    
    tanggal_waktu = fields.Datetime(string='Kapan & Jam')
    notes = fields.Text(string='Catatan')
    materi_id = fields.Many2one('modul.pembelajaran.line', string='Materi')

    google_drive_folder_url = fields.Char(string='Folder Google Drive', readonly=True, copy=False)
    
    drive_attachment_ids = fields.One2many(
        'absensi.drive.attachment',
        'absensi_line_id',
        string='File Bukti'
    )

    def action_upload_files_to_drive(self):
        # Logika untuk upload file ke Google Drive akan ditambahkan di sini.
        # Untuk saat ini, kita bisa tambahkan placeholder atau wizard.
        self.ensure_one()
        # Placeholder action
        return {
            'type': 'ir.actions.act_window',
            'name': 'Upload Foto/Video',
            'res_model': 'upload.wizard', # Nama wizard yang akan kita buat
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_absensi_line_id': self.id,
            }
        }

    def action_view_drive_files(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'File Bukti',
            'res_model': 'absensi.drive.attachment',
            'view_mode': 'kanban,tree,form',
            'domain': [('absensi_line_id', '=', self.id)],
            'context': {'default_absensi_line_id': self.id},
        }

    display_name = fields.Char(string='Judul Pertemuan', compute='_compute_display_name', store=True)

    @api.depends('materi_id.name', 'tanggal_waktu')
    def _compute_display_name(self):
        for rec in self:
            materi_name = rec.materi_id.name if rec.materi_id else "Materi Belum Dipilih"
            tanggal_str = ""
            if rec.tanggal_waktu:
                tanggal_str = rec.tanggal_waktu.strftime('%d/%m/%Y %H:%M')
            rec.display_name = f"{materi_name} - {tanggal_str}" if tanggal_str else materi_name
    
    # Fungsi _check_tanggal_waktu tidak perlu diubah
    @api.constrains('tanggal_waktu', 'pertemuan_ke')
    def _check_tanggal_waktu(self):
        # ... (Kode validasi tanggal tetap sama)
        for line in self:
            if not line.tanggal_waktu:
                continue
            prev_line = self.search([
                ('absensi_id', '=', line.absensi_id.id),
                ('pertemuan_ke', '=', line.pertemuan_ke - 1),
                ('tanggal_waktu', '!=', False)
            ], limit=1)
            if prev_line and line.tanggal_waktu < prev_line.tanggal_waktu:
                raise ValidationError(_(
                    "Tanggal Pertemuan ke-%s tidak boleh sebelum Pertemuan ke-%s (%s)"
                ) % (line.pertemuan_ke, prev_line.pertemuan_ke, prev_line.tanggal_waktu))
            next_line = self.search([
                ('absensi_id', '=', line.absensi_id.id),
                ('pertemuan_ke', '=', line.pertemuan_ke + 1),
                ('tanggal_waktu', '!=', False)
            ], limit=1)
            if next_line and line.tanggal_waktu > next_line.tanggal_waktu:
                raise ValidationError(_(
                    "Tanggal Pertemuan ke-%s tidak boleh setelah Pertemuan ke-%s (%s)"
                ) % (line.pertemuan_ke, next_line.pertemuan_ke, next_line.tanggal_waktu))