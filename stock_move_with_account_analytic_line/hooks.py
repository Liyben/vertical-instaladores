import logging
from odoo import _, api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

def _pre_init_hook_reset_valuation(cr):
    """
    This hook runs BEFORE the module is loaded.
    Its job is to set a "safe" value on the 'All' category
    so that modules like 'l10n_es' do not fail during the update.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    param_model = env['ir.config_parameter'].sudo()
    all_category = env.ref('product.product_category_all', raise_if_not_found=False)
    
    if all_category and all_category.property_valuation == 'only_analytic':
        _logger.info(_("HOOK (PRE): 'only_analytic' detected. Changing to 'manual_periodic' for update."))
        all_category.write({'property_valuation': 'manual_periodic'})
        
        param_model.set_param('stock_move_with_account_analytic_line.restaurar_analytic_all', 'True')
    else:
        param_model.set_param('stock_move_with_account_analytic_line.restaurar_analytic_all', 'False')

def _post_init_hook_restore_valuation(cr, registry):
    """
    This hook runs AFTER the module is loaded.
    The 'selection_add' is now applied, so 'only_analytic' is valid.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    param_model = env['ir.config_parameter'].sudo()
    param_value = param_model.get_param('stock_move_with_account_analytic_line.restaurar_analytic_all')

    if param_value == 'True':
        _logger.info(_("HOOK (POST): Restoring 'only_analytic' on 'All' category."))
        all_category = env.ref('product.product_category_all', raise_if_not_found=False)
        if all_category:
            all_category.write({'property_valuation': 'only_analytic'})
        
        param_model.set_param('stock_move_with_account_analytic_line.restaurar_analytic_all', 'False')