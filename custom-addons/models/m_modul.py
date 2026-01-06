from odoo import models, fields, api

class ModulPembelajaran(models.Model):
    _name = 'modul.pembelajaran'
    _description = 'Modul Pembelajaran'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char("Judul", required=True, tracking=True)
    link_materi = fields.Char("Link Materi (Google Drive)")
    materi_ids = fields.One2many('modul.pembelajaran.line', 'modul_id', string="Materi")

class ModulPembelajaranLine(models.Model):
    _name = 'modul.pembelajaran.line'
    _description = 'Materi Pembelajaran'

    modul_id = fields.Many2one('modul.pembelajaran', string="Modul")
    name = fields.Char("Materi", required=True)
    description = fields.Text("Deskripsi")