# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class StudentProfileAbsensiExtension(models.Model):
    _inherit = 'm.siswa'

    # Relasi ke Lembar Absensi (untuk keperluan kalkulasi)
    absensi_sheet_ids = fields.One2many(
        'absensi.siswa.absensi',
        'siswa_id',
        string="Lembar Absensi"
    )

    @api.depends('absensi_sheet_ids.attendance_line_ids')
    def _compute_jumlah_pertemuan_hadir(self):
        _logger.info("Memulai kalkulasi _compute_jumlah_pertemuan_hadir...")
        for student in self:
            _logger.info(f"Menghitung untuk siswa: {student.name}")
            if not student.absensi_sheet_ids:
                _logger.warning(f"Siswa {student.name} tidak punya lembar absensi (absensi_sheet_ids). Dihitung sebagai 0.")
                student.jumlah_pertemuan_hadir = 0
                continue

            _logger.info(f"Lembar absensi ditemukan: {student.absensi_sheet_ids.ids}")
            
            # Menghitung semua baris absensi, tidak peduli statusnya
            all_lines = student.absensi_sheet_ids.mapped('attendance_line_ids')
            line_count = len(all_lines)
            
            _logger.info(f"Jumlah baris absensi yang ditemukan: {line_count}")
            student.jumlah_pertemuan_hadir = line_count

    # Override the original field to make it computed and stored
    jumlah_pertemuan_hadir = fields.Integer(
        string='Total Pertemuan Dihadiri',
        compute='_compute_jumlah_pertemuan_hadir',
        store=True, # store=True agar nilainya tersimpan di database dan bisa dicari
        readonly=True,
    )
