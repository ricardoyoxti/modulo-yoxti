from odoo import models, fields, api
import json
import base64
from datetime import datetime
class CustomerExportWizard(models.TransientModel):
_name = 'customer.export.wizard'
_description = 'Wizard para Exportar Clientes a JSON'
date_from = fields.Date('Fecha Desde', required=True)
date_to = fields.Date('Fecha Hasta', required=True)
partner_ids = fields.Many2many('res.partner', string='Clientes')
include_coordinates = fields.Boolean('Incluir Coordenadas', default=True)
order_states = fields.Selection([
    ('draft', 'Borrador'),
    ('sent', 'Enviado'),
    ('sale', 'Confirmado'),
    ('done', 'Completado'),
    ('cancel', 'Cancelado'),
    ('all', 'Todos los estados')
], default='sale', string='Estados de Pedido')

def action_export_json(self):
    """Exporta los datos a JSON"""
    # Construir dominio de búsqueda
    domain = [
        ('date_order', '>=', self.date_from),
        ('date_order', '<=', self.date_to)
    ]
    
    if self.partner_ids:
        domain.append(('partner_id', 'in', self.partner_ids.ids))
    
    if self.order_states != 'all':
        domain.append(('state', '=', self.order_states))

    # Buscar pedidos
    orders = self.env['sale.order'].search(domain)
    
    if not orders:
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Sin datos',
                'message': 'No se encontraron pedidos con los criterios especificados.',
                'type': 'warning',
            }
        }

    # Preparar datos
    customer_data = orders._prepare_customer_json_data(orders)
    
    # Generar JSON
    json_data = json.dumps(customer_data, ensure_ascii=False, indent=2)
    filename = f"customers_export_{self.date_from}_{self.date_to}.json"
    
    # Crear attachment
    attachment = self.env['ir.attachment'].create({
        'name': filename,
        'type': 'binary',
        'datas': base64.b64encode(json_data.encode('utf-8')),
        'res_model': 'customer.export.wizard',
        'res_id': self.id,
        'mimetype': 'application/json',
    })

    return {
        'type': 'ir.actions.act_url',
        'url': f'/web/content/{attachment.id}/{filename}?download=true',
        'target': 'self',
    }