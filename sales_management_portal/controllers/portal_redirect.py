from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal
import logging

_logger = logging.getLogger(__name__)

class MasterPortalRedirect(CustomerPortal):
    """
    Master controller that overrides portal routes and adds custom redirects
    """
    
    @http.route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        """Override portal home - this should take precedence"""
        _logger.info(f"MASTER REDIRECT: Portal home override for user {request.env.user.id}")
        return request.redirect('/sales_management')