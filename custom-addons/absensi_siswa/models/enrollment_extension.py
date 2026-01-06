# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class StudentCourseEnrollmentExtension(models.Model):
    _inherit = 'siswa.kursus.enrollment'

    absensi_ids = fields.One2many(
        'absensi.siswa.absensi', 
        'enrollment_id',
        string='Lembar Absensi'
    )

    jumlah_pertemuan_diikuti = fields.Integer(
        string="Pertemuan Diikuti",
        compute='_compute_jumlah_pertemuan_diikuti',
        store=True
    )

    @api.depends('absensi_ids.attendance_line_ids')
    def _compute_jumlah_pertemuan_diikuti(self):
        for enrollment in self:
            enrollment.jumlah_pertemuan_diikuti = len(enrollment.absensi_ids.mapped('attendance_line_ids'))

    @api.model
    def create(self, vals):
        """
        Saat enrollment baru dibuat, otomatis buatkan juga lembar absensi kosongnya.
        """
        enrollment = super(StudentCourseEnrollmentExtension, self).create(vals)
        if not enrollment.absensi_ids:
            self.env['absensi.siswa.absensi'].create({
                'enrollment_id': enrollment.id,
            })
        return enrollment

class AbsensiSiswaLineExtension(models.Model):
    _inherit = 'absensi.siswa.absensi.line'