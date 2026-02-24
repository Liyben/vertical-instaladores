# © 2026 Seges
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, SUPERUSER_ID

def pre_init_hook(env):
    """
    Pre-crea la columna y asigna el ID para evitar que el _sql_constraints
    de unicidad haga fallar la instalación del módulo si hay registros previos.
    """
    # 1. Creamos la columna si no existe (buena práctica por si se reinstala)
    env.cr.execute("""
        ALTER TABLE hr_contract 
        ADD COLUMN IF NOT EXISTS code character varying;
    """)
    # 2. Asignamos el ID convertido a texto
    env.cr.execute("UPDATE hr_contract SET code = id::varchar WHERE code IS NULL OR code = '/';")


def post_init_hook(env):
    """
    Asigna la secuencia real a los contratos que ya existían.
    """
    contract_obj = env["hr.contract"].with_context(active_test=False) # ¡Incluir archivados!
    sequence_obj = env["ir.sequence"]
    
    # Buscamos contratos (ahora tienen su ID como código gracias al pre_init)
    contracts = contract_obj.search([], order="id")
    
    for contract_id in contracts.ids:
        # Uso de SQL cr.execute aquí es excelente para el rendimiento
        # en migraciones/instalaciones masivas en lugar de usar el ORM.
        env.cr.execute(
            "UPDATE hr_contract SET code = %s WHERE id = %s;",
            (
                sequence_obj.next_by_code("hr.contract"),
                contract_id,
            ),
        )