{
'name': 'Sale Customer JSON Export',
'version': '1.0.0',
'category': 'Sales',
'summary': 'Botón para exportar clientes con pedidos a JSON desde el módulo de ventas',
'description': """
Agrega funcionalidad de exportación JSON directamente en el módulo de ventas.
- Botón en la vista de pedidos de venta
- Exportación masiva desde lista de pedidos
- Incluye coordenadas geográficas de clientes
""",
'author': 'Tu Empresa',
'depends': ['sale', 'base'],
'data': [
'security/ir.model.access.csv',
'views/sale_order_views.xml',
'wizard/customer_export_wizard_views.xml',
],
'installable': True,
'application': False,
'auto_install': False,
}