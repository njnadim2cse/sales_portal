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
        """Override portal home - redirect to sales management dashboard"""
        _logger.info(f"MASTER REDIRECT: Portal home override for user {request.env.user.id}")
        
        # Check if user has access to any portal
        user = request.env.user
        if not (user.use_contact_portal or user.use_todo_portal or user.use_quotation_portal):
            # If no portal access, redirect to web home
            return request.redirect('/web')
        
        # Redirect to sales management dashboard
        return request.redirect('/sales_management')
    
    # Also override the account route to prevent conflicts
    @http.route('/my/account', type='http', auth='user', website=True)
    def account(self, **kw):
        """Override account page to avoid conflicts"""
        return super(MasterPortalRedirect, self).account(**kw)