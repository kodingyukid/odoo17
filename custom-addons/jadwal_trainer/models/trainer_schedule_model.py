from odoo import models, fields, api
import datetime

class TrainerSchedule(models.Model):
    _name = 'trainer.schedule' # <--- PASTIKAN INI SAMA DENGAN DI ATAS
    _description = 'Jadwal Pertemuan Trainer'
    _order = 'date desc'

    name = fields.Char(string='Deskripsi') # Simple Char field, not computed

    def _generate_name(self, student, date):
        display_name_parts = []
        if student and student.display_name:
            display_name_parts.append(student.display_name)
        
        if date and isinstance(date, (datetime.datetime, datetime.date)):
            display_name_parts.append(date.strftime('%d/%m/%Y'))
        
        if display_name_parts:
            return " - ".join(display_name_parts)
        return '' # Return empty string if no parts

    @api.model
    def create(self, vals):
        if 'name' not in vals or not vals['name']:
            student = self.env['res.partner'].browse(vals.get('student_id'))
            date = vals.get('date')
            vals['name'] = self._generate_name(student, date)
        return super(TrainerSchedule, self).create(vals)

    def write(self, vals):
        # If student_id or date changes, and name is not explicitly provided, regenerate name
        if 'student_id' in vals or 'date' in vals:
            for record in self:
                student = self.env['res.partner'].browse(vals.get('student_id') or record.student_id.id)
                date = vals.get('date') or record.date
                if 'name' not in vals or not vals['name']: # Only regenerate if name is not explicitly set in vals
                    vals['name'] = self._generate_name(student, date)
        return super(TrainerSchedule, self).write(vals)
    
    student_id = fields.Many2one(
        'res.partner', 
        string='Siswa', 
        required=True, 
        ondelete='cascade',
        field_attrs={'readonly': [('student_id', '!=', False)]}
    )
    
    trainer_id = fields.Many2one(
        'res.users', 
        string='Trainer', 
        default=lambda self: self.env.user,
        required=True
    )
    
    date = fields.Datetime( # <--- FIELD INI YANG DICARI OLEH XML
        string='Tanggal Pertemuan', 
        default=fields.Datetime.now,
        required=True
    )
    
    notes = fields.Text('Notes (Opsional)')

    meeting_number = fields.Selection([
        (str(i), str(i)) for i in range(1, 21)
    ], string='Pertemuan Ke-', default='1', required=True)

    class_type = fields.Selection([
        ('scratch', 'Scratch'),
        ('scratch_jr', 'Scratch Jr'),
        ('pictoblox', 'Pictoblox'),
        ('merakit', 'Merakit'),
    ], string='Kelas', required=True)

    is_recurrent = fields.Boolean(string='Is Recurrent', default=False)
    recurrence_id = fields.Many2one('trainer.schedule.recurrence', string='Recurrence Series', ondelete='cascade')
    
    # Recurrence Rule Fields (copied from recurrence wizard/model for convenience)
    recurrence_rule_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], string='Recurrence Type', default='weekly')
    recurrence_interval = fields.Integer(string='Repeat Every', default=1)
    recurrence_end_type = fields.Selection([
        ('count', 'Number of Occurrences'),
        ('end_date', 'End Date'),
    ], string='Recurrence End Type', default='count')
    recurrence_count = fields.Integer(string='Number of Occurrences', default=1)
    recurrence_end_date = fields.Date(string='Recurrence End Date')


class TrainerScheduleRecurrence(models.Model):
    _name = 'trainer.schedule.recurrence'
    _description = 'Trainer Schedule Recurrence'

    name = fields.Char(string='Recurrence Name', compute='_compute_name', store=True)
    schedule_ids = fields.One2many('trainer.schedule', 'recurrence_id', string='Schedules')
    first_schedule_id = fields.Many2one('trainer.schedule', string='First Schedule', ondelete='cascade')

    # Recurrence Rule Fields
    rule_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], string='Recurrence Type', default='weekly', required=True)
    interval = fields.Integer(string='Repeat Every', default=1, required=True)
    end_type = fields.Selection([
        ('count', 'Number of Occurrences'),
        ('end_date', 'End Date'),
    ], string='Recurrence End Type', default='count', required=True)
    count = fields.Integer(string='Number of Occurrences', default=1)
    end_date = fields.Date(string='Recurrence End Date')

    @api.depends('first_schedule_id.student_id', 'first_schedule_id.date', 'rule_type')
    def _compute_name(self):
        for record in self:
            if record.first_schedule_id and record.first_schedule_id.student_id and record.first_schedule_id.date:
                record.name = f"Recurrence for {record.first_schedule_id.student_id.display_name} - {record.first_schedule_id.date.strftime('%Y-%m-%d')} ({record.rule_type.capitalize()})"
            else:
                record.name = "New Recurrence Series"

    is_recurrent = fields.Boolean(string='Is Recurrent', default=False)
    recurrence_id = fields.Many2one('trainer.schedule.recurrence', string='Recurrence Series', ondelete='cascade')
    
    # Recurrence Rule Fields (copied from recurrence wizard/model for convenience)
    recurrence_rule_type = fields.Selection([
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ], string='Recurrence Type', default='weekly')
    recurrence_interval = fields.Integer(string='Repeat Every', default=1)
    recurrence_end_type = fields.Selection([
        ('count', 'Number of Occurrences'),
        ('end_date', 'End Date'),
    ], string='Recurrence End Type', default='count')
    recurrence_count = fields.Integer(string='Number of Occurrences', default=1)
    recurrence_end_date = fields.Date(string='Recurrence End Date')