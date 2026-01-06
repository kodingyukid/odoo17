from odoo import models, fields, api
from datetime import timedelta, datetime
import calendar

class HrAttendancePerformanceRule(models.Model):
    _name = 'hr.attendance.performance.rule'
    _description = 'Performance Evaluation Rules'
    _order = 'min_hours desc'

    name = fields.Char('Status Name', required=True, help="e.g. LULUS (Excellent)")
    min_hours = fields.Float('Min Average Hours/Week', required=True, default=0.0)
    max_hours = fields.Float('Max Average Hours/Week', required=True, default=168.0, help="Exclusive upper bound")
    
    _sql_constraints = [
        ('min_max_check', 'CHECK(min_hours < max_hours)', 'Min Hours must be less than Max Hours'),
    ]

class HrAttendancePerformance(models.Model):
    _name = 'hr.attendance.performance'
    _description = 'Attendance Performance Evaluation'
    _rec_name = 'employee_id'
    _order = 'create_date desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required=True)
    
    line_ids = fields.One2many('hr.attendance.performance.line', 'performance_id', string='Monthly Details', readonly=True)
    
    total_hours = fields.Float('Total Hours', readonly=True, store=True)
    duration_weeks = fields.Float('Duration (Weeks)', readonly=True, digits=(16, 2), store=True)
    average_weekly_hours = fields.Float('Average Hours/Week', readonly=True, digits=(16, 2), store=True)
    
    status_rule_id = fields.Many2one('hr.attendance.performance.rule', string='Performance Status', readonly=True, store=True)
    notes = fields.Text('Notes', help="Additional notes for the report (e.g. Recommendations)")
    
    def action_calculate(self):
        for record in self:
            # Clear existing lines
            record.line_ids.unlink()
            
            # Search Attendance
            start_dt = fields.Datetime.to_datetime(record.start_date)
            end_dt = fields.Datetime.to_datetime(record.end_date) + timedelta(days=1, seconds=-1)
            
            domain = [
                ('employee_id', '=', record.employee_id.id),
                ('check_in', '>=', start_dt),
                ('check_in', '<=', end_dt),
                ('check_out', '!=', False)
            ]
            attendances = self.env['hr.attendance'].search(domain)
            
            # Calculate
            total_hours = 0.0
            monthly_data = {}
            
            for att in attendances:
                hours = att.worked_hours
                total_hours += hours
                
                # Month grouping
                month_key = att.check_in.strftime('%B %Y')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = 0.0
                monthly_data[month_key] += hours

            # Create Lines
            sorted_keys = sorted(monthly_data.keys(), key=lambda x: datetime.strptime(x, '%B %Y') if ' ' in x else x)
            
            lines = []
            for month in sorted_keys:
                # Calculate Monthly Average
                # Parse Month Year to get days in month
                try:
                    dt_month = datetime.strptime(month, '%B %Y')
                    days_in_month = calendar.monthrange(dt_month.year, dt_month.month)[1]
                    weeks_in_month = days_in_month / 7.0
                    avg_weekly = monthly_data[month] / weeks_in_month if weeks_in_month > 0 else 0.0
                except:
                    avg_weekly = 0.0

                lines.append((0, 0, {
                    'month_name': month,
                    'total_hours': monthly_data[month],
                    'average_weekly_hours': avg_weekly,
                }))
            record.line_ids = lines
            
            # Stats
            record.total_hours = total_hours
            
            # Calc Weeks
            weeks = 0.0
            if record.start_date and record.end_date:
                delta = record.end_date - record.start_date
                days = delta.days + 1
                weeks = days / 7.0
                record.duration_weeks = weeks
                
            if weeks > 0:
                record.average_weekly_hours = total_hours / weeks
            else:
                record.average_weekly_hours = 0.0
            
            # Determine Status
            rule = self.env['hr.attendance.performance.rule'].search([
                ('min_hours', '<=', record.average_weekly_hours),
                ('max_hours', '>', record.average_weekly_hours)
            ], limit=1, order='min_hours desc')
            
            if not rule and record.average_weekly_hours >= 0:
                 highest_rule = self.env['hr.attendance.performance.rule'].search([], order='max_hours desc', limit=1)
                 if highest_rule and record.average_weekly_hours >= highest_rule.max_hours:
                     pass
            
            record.status_rule_id = rule

class HrAttendancePerformanceLine(models.Model):
    _name = 'hr.attendance.performance.line'
    _description = 'Performance Monthly Detail'
    
    performance_id = fields.Many2one('hr.attendance.performance', required=True, ondelete='cascade')
    month_name = fields.Char('Month', required=True)
    total_hours = fields.Float('Total Hours', readonly=True)
    average_weekly_hours = fields.Float('Avg Hours/Week', readonly=True, digits=(16, 2))
