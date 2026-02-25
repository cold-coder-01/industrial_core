from odoo import models, fields, api, _
class AddisProduction(models.Model):
    _name="addis.production"
    _description="Addis Industrial production Order"
    _inherit=['mail.thread', 'mail.activity.mixin']
    _order = "date_planned desc"

    name = fields.Char(
        string="Order Reference", 
        required=True, copy=False, readonly=True,default=lambda self: _('New')
        )
                     
    state= fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('progress', 'In Progress'),
        ('done', 'Finished'),
        ('cancel', 'Canceled'),
    ], string="status", default='draft', tracking=True)
    responsible_id= fields.Many2one('hr.employee', string="Production Supervisor", required=True)
    partner_id= fields.Many2one('res.partner', string="Wholesale Client")
    invoice_id= fields.Many2one('account.move', string="Generated Invoice", readonly=True)
    date_planned= fields.Datetime(string="Planned Date", default=fields.Datetime.now)
    product_name= fields.Char(string="Product To Produce", required= True)
    raw_material_input= fields.Float(string="Input Quantity (kg)", tracking=True)
    finished_output= fields.Float(string="Output Quantity (kg)", tracking= True)
    waste_percentage= fields.Float(string="Waste Percentage", compute= "_compute_waste_percentage", store=True)
    @api.depends('raw_material_input', 'finished_output')
    def _compute_waste_percentage(self):
        for record in self:
            if record.raw_material_input > 0:
                loss = record.raw_material_input - record.finished_output
                record.waste_percentage= (loss / record.raw_material_input) 
            else:
                record.waste_percentage= 0.0
    def action_confirm(self):
        self.state= 'confirmed'
    def action_done(self):
        if self.finished_output <= 0:
            raise UserError(_("You can not finish an order with zero output!"))
        self.state='done'
    def action_create_industrial_invoice(self):
        for record in self:
            if not record.partner_id:
                raise UserError(_("plz select the wholesale client first"))
            invoice = self.env['account.move'].create({
                'partner_id': record.partner_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': [(0, 0, {
                    'name': f"Production of {record.product_name}",
                    'quantity': record.finished_output,
                    'price_unit': 1000.0, # Example price in Birr
                })],
            })
            record.invoice_id = invoice.id
            return {
                'name': _('Production Invoice'),
                'view_mode': 'form',
                'res_model': 'account.move',
                'res_id': invoice.id,
                'type': 'ir.actions.act_window',
                'target': 'current',
            }