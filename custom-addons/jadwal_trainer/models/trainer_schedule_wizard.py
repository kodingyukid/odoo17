from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
import datetime

class TrainerScheduleRecurrenceWizard(models.TransientModel):
    _name = 'trainer.schedule.recurrence.wizard'
    _description = 'Trainer Schedule Recurrence Wizard'

    schedule_id = fields.Many2one('trainer.schedule', string='Original Schedule', required=True, ondelete='cascade')

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

    @api.onchange('rule_type')
    def _onchange_rule_type(self):
        if self.rule_type == 'weekly':
            self.interval = 1
        elif self.rule_type == 'monthly':
            self.interval = 1
        elif self.rule_type == 'yearly':
            self.interval = 1
        else:
            self.interval = 1

    def action_generate_recurrence(self):
        self.ensure_one()
        original_schedule = self.schedule_id

        # Create a new recurrence record
        recurrence = self.env['trainer.schedule.recurrence'].create({
            'first_schedule_id': original_schedule.id,
            'rule_type': self.rule_type,
            'interval': self.interval,
            'end_type': self.end_type,
            'count': self.count,
            'end_date': self.end_date,
        })

        # Update the original schedule to be part of this recurrence
        original_schedule.write({
            'is_recurrent': True,
            'recurrence_id': recurrence.id,
            'recurrence_rule_type': self.rule_type,
            'recurrence_interval': self.interval,
            'recurrence_end_type': self.end_type,
            'recurrence_count': self.count,
            'recurrence_end_date': self.end_date,
        })
        recurrence.write({'schedule_ids': [(4, original_schedule.id)]})

        # Generate new schedules
        new_schedules = []
        current_date = original_schedule.date
        
        # Determine the end condition
        if self.end_type == 'count':
            # Subtract 1 because the original schedule is already the first occurrence
            num_occurrences_to_generate = self.count - 1 
        else: # end_type == 'end_date'
            num_occurrences_to_generate = float('inf') # Generate until end_date

        generated_count = 0
        while generated_count < num_occurrences_to_generate:
            if self.rule_type == 'daily':
                current_date += relativedelta(days=self.interval)
            elif self.rule_type == 'weekly':
                current_date += relativedelta(weeks=self.interval)
            elif self.rule_type == 'monthly':
                current_date += relativedelta(months=self.interval)
            elif self.rule_type == 'yearly':
                current_date += relativedelta(years=self.interval)
            
            # Check end date condition if applicable
            if self.end_type == 'end_date' and current_date.date() > self.end_date:
                break

            # Create new schedule record
            new_schedule_vals = {
                'student_id': original_schedule.student_id.id,
                'trainer_id': original_schedule.trainer_id.id,
                'date': current_date,
                'meeting_number': original_schedule.meeting_number,
                'class_type': original_schedule.class_type,
                'notes': original_schedule.notes,
                'is_recurrent': True,
                'recurrence_id': recurrence.id,
                'recurrence_rule_type': self.rule_type,
                'recurrence_interval': self.interval,
                'recurrence_end_type': self.end_type,
                'recurrence_count': self.count,
                'recurrence_end_date': self.end_date,
            }
            new_schedule = self.env['trainer.schedule'].create(new_schedule_vals)
            new_schedules.append(new_schedule.id)
            generated_count += 1
        
        # Link generated schedules to the recurrence record
        if new_schedules:
            recurrence.write({'schedule_ids': [(4, sid) for sid in new_schedules]})

        return {'type': 'ir.actions.act_window_close'}