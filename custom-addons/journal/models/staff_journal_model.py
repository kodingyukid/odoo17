from odoo import models, fields, api


class StaffJournalModel(models.Model):
    _name = "staff.journal"
    _description = "Jurnal Harian Staff"
    _order = "date desc"

    # =====================
    # RELATION
    # =====================
    attendance_id = fields.Many2one(
        "hr.attendance",
        string="Attendance",
        ondelete="cascade",
        readonly=True
    )

    employee_id = fields.Many2one(
        "hr.employee",
        string="Pegawai",
        required=True,
        readonly=True
    )

    department_id = fields.Many2one(
        "hr.department",
        string="Divisi",
        related="employee_id.department_id",
        store=True,
        readonly=True
    )

    # =====================
    # TIME (AUTO FROM ATTENDANCE)
    # =====================
    date = fields.Date(
        string="Tanggal",
        readonly=True
    )

    check_in = fields.Datetime(
        string="Jam Masuk",
        readonly=True
    )

    check_out = fields.Datetime(
        string="Jam Keluar",
        readonly=True
    )

    work_duration = fields.Float(
        string="Durasi Kerja (Jam)",
        compute="_compute_work_duration",
        store=True,
        readonly=True
    )

    # =====================
    # JOURNAL CONTENT
    # =====================
    target_today = fields.Text(string="Target Hari Ini")
    progress_today = fields.Text(string="Progress Hari Ini")
    obstacles = fields.Text(
        string="Kendala / Hambatan",
        default="Tidak ada"
    )
    plan_tomorrow = fields.Text(string="Rencana Besok")
    additional_notes = fields.Text(string="Catatan Tambahan")

    # =====================
    # STATUS
    # =====================
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("approved", "Approved"),
        ],
        default="draft",
        string="Status"
    )

    # =====================
    # COMPUTE
    # =====================
    @api.depends("check_in", "check_out")
    def _compute_work_duration(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                delta = rec.check_out - rec.check_in
                rec.work_duration = delta.total_seconds() / 3600
            else:
                rec.work_duration = 0.0

    # =====================
    # ACTIONS
    # =====================
    def action_submit(self):
        self.write({"state": "submitted"})

    def action_approve(self):
        self.write({"state": "approved"})

    @api.model
    def create_today_journal(self):
        # This is a placeholder for the actual implementation
        pass

    # =====================
    # CONSTRAINT
    # =====================
    _sql_constraints = [
        (
            "unique_attendance_journal",
            "unique(attendance_id)",
            "Satu attendance hanya boleh memiliki satu jurnal."
        )
    ]
