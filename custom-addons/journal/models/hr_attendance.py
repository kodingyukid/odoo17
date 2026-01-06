from odoo import models, fields, api


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    journal_id = fields.Many2one(
        "staff.journal",
        string="Daily Journal",
        readonly=True
    )

    @api.model
    def create(self, vals):
        res = super(HrAttendance, self).create(vals)
        if "check_out" in vals:
            if res.check_out and not res.journal_id:
                journal = self.env["staff.journal"].create({
                    "attendance_id": res.id,
                    "employee_id": res.employee_id.id,
                    "date": res.check_in.date(),
                    "check_in": res.check_in,
                    "check_out": res.check_out,
                })
                res.journal_id = journal.id
        return res

    def write(self, vals):
        res = super().write(vals)

        # Trigger saat CHECK OUT
        if "check_out" in vals:
            for att in self:
                if att.check_out and not att.journal_id:
                    journal = self.env["staff.journal"].create({
                        "attendance_id": att.id,
                        "employee_id": att.employee_id.id,
                        "date": att.check_in.date(),
                        "check_in": att.check_in,
                        "check_out": att.check_out,
                    })
                    att.journal_id = journal.id

        return res
