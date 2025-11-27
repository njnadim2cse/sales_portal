import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class SalesPortalController(http.Controller):

    @http.route('/sales_management', type='http', auth='user', website=True)
    def sales_management_home(self, **kw):
        """Sales Management Dashboard Home"""
        # Check if user has access to any portal
        if not (request.env.user.use_contact_portal or 
                request.env.user.use_todo_portal or 
                request.env.user.use_quotation_portal):
            return request.redirect('/web')
        
        # Pass portal access flags to template for sidebar logic
        return request.render('sales_management_portal.dashboard_main', {
            'user_has_contact_portal': request.env.user.use_contact_portal,
            'user_has_todo_portal': request.env.user.use_todo_portal,
            'user_has_quotation_portal': request.env.user.use_quotation_portal,
        })

    @http.route('/sales_management/contacts', type='http', auth='user', website=True)
    def contacts_dashboard(self, **kw):
        """Contacts List View"""
        # Check portal access
        if not request.env.user.use_contact_portal:
            return request.redirect('/sales_management')
        
        # Get contacts where the current user is the salesman
        user_id = request.env.user.id
        contacts = request.env['res.partner'].sudo().search([
            ('user_id', '=', user_id)
        ])
        
        # Handle search
        search_term = kw.get('search', '')
        if search_term:
            contacts = contacts.filtered(lambda c: 
                search_term.lower() in (c.name or '').lower() or
                search_term.lower() in (c.email or '').lower() or
                search_term.lower() in (c.phone or '').lower() or
                search_term.lower() in (c.city or '').lower() or
                search_term.lower() in (c.state_id.name or '').lower() or
                search_term.lower() in (c.country_id.name or '').lower()
            )
        
        # Pass portal access flags to template for sidebar logic
        return request.render('sales_management_portal.contacts_list', {
            'contacts': contacts,
            'search_term': search_term,
            'user_has_contact_portal': request.env.user.use_contact_portal,
            'user_has_todo_portal': request.env.user.use_todo_portal,
            'user_has_quotation_portal': request.env.user.use_quotation_portal,
        })

    @http.route('/sales_management/contacts/create', type='http', auth='user', website=True)
    def create_contact_form(self, **kw):
        """Display contact creation form"""
        # Check portal access
        if not request.env.user.use_contact_portal:
            return request.redirect('/sales_management')
        
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        tags = request.env['res.partner.category'].sudo().search([])
        companies = request.env['res.partner'].sudo().search([
            ('is_company', '=', True),
            ('user_id', '=', request.env.user.id)
        ])
        
        # Pass portal access flags to template for sidebar logic
        return request.render('sales_management_portal.contact_form', {
            'countries': countries,
            'states': states,
            'tags': tags,
            'companies': companies,
            'user_has_contact_portal': request.env.user.use_contact_portal,
            'user_has_todo_portal': request.env.user.use_todo_portal,
            'user_has_quotation_portal': request.env.user.use_quotation_portal,
        })

    @http.route('/sales_management/contacts/submit', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def submit_contact(self, **kw):
        """Handle contact form submission"""
        try:
            # Check portal access
            if not request.env.user.use_contact_portal:
                return request.redirect('/sales_management')
            
            current_user_id = request.env.user.id
            
            if kw.get('company_type') == 'company':
                # Create company
                company_data = {
                    'name': kw.get('name'),
                    'email': kw.get('email'),
                    'phone': kw.get('phone'),
                    'is_company': True,
                    'street': kw.get('street'),
                    'street2': kw.get('street2'),
                    'city': kw.get('city'),
                    'state_id': int(kw.get('state_id')) if kw.get('state_id') else False,
                    'zip': kw.get('zip'),
                    'country_id': int(kw.get('country_id')) if kw.get('country_id') else False,
                    'user_id': current_user_id,
                }
                
                # Handle tags
                if kw.get('category_id'):
                    company_data['category_id'] = [(6, 0, [int(kw.get('category_id'))])]
                    
                company = request.env['res.partner'].sudo().create(company_data)
                _logger.info(f"Created company: {company.name}")
                
                # Handle child contacts (contact persons) - FIXED VERSION
                child_names = kw.getlist('child_name[]')
                child_emails = kw.getlist('child_email[]')
                child_phones = kw.getlist('child_phone[]')
                child_functions = kw.getlist('child_function[]')
                
                created_children = 0
                for i in range(len(child_names)):
                    if child_names[i] and child_names[i].strip():  # Only create if name exists and not empty
                        child_data = {
                            'name': child_names[i].strip(),
                            'email': child_emails[i] or False,
                            'phone': child_phones[i] or False,
                            'function': child_functions[i] or False,
                            'type': 'contact',
                            'user_id': current_user_id,
                            'is_company': False,
                            'parent_id': company.id,  # This links to parent company
                        }
                        child_contact = request.env['res.partner'].sudo().create(child_data)
                        created_children += 1
                        _logger.info(f"Created child contact: {child_contact.name} for company: {company.name}")
                
                _logger.info(f"Successfully created company '{company.name}' with {created_children} contact persons")
                
            else:  # Person type
                contact_data = {
                    'name': kw.get('name'),
                    'email': kw.get('email'),
                    'phone': kw.get('phone'),
                    'is_company': False,
                    'function': kw.get('function', ''),  # Job title for person
                    'street': kw.get('street'),
                    'street2': kw.get('street2'),
                    'city': kw.get('city'),
                    'state_id': int(kw.get('state_id')) if kw.get('state_id') else False,
                    'zip': kw.get('zip'),
                    'country_id': int(kw.get('country_id')) if kw.get('country_id') else False,
                    'user_id': current_user_id,
                }
                
                # Handle tags
                if kw.get('category_id'):
                    contact_data['category_id'] = [(6, 0, [int(kw.get('category_id'))])]
                
                # If company is selected from dropdown
                company_id = kw.get('company_id')
                if company_id and company_id != 'new' and company_id != '':
                    contact_data['parent_id'] = int(company_id)
                    # Copy address from company if no address provided
                    company = request.env['res.partner'].sudo().browse(int(company_id))
                    if not kw.get('street') and company.street:
                        contact_data.update({
                            'street': company.street,
                            'street2': company.street2,
                            'city': company.city,
                            'state_id': company.state_id.id,
                            'zip': company.zip,
                            'country_id': company.country_id.id,
                        })
                        # Copy tags from company if no tags selected
                        if not kw.get('category_id') and company.category_id:
                            contact_data['category_id'] = [(6, 0, company.category_id.ids)]
                
                person_contact = request.env['res.partner'].sudo().create(contact_data)
                _logger.info(f"Created person contact: {person_contact.name}")
            
            # Redirect with success message
            return request.redirect('/sales_management/contacts?success=1')
            
        except Exception as e:
            _logger.error(f"Error creating contact: {str(e)}")
            return request.redirect('/sales_management/contacts/create?error=1')

    @http.route('/sales_management/contacts/view/<int:contact_id>', type='http', auth='user', website=True)
    def view_contact(self, contact_id, **kw):
        """View individual contact details"""
        # Check portal access
        if not request.env.user.use_contact_portal:
            return request.redirect('/sales_management')
        
        contact = request.env['res.partner'].sudo().browse(contact_id)
        
        # Security check - ensure user can only view their own contacts
        if contact.user_id.id != request.env.user.id:
            return request.redirect('/sales_management/contacts')
        
        # Get child contacts for companies
        child_contacts = []
        if contact.is_company:
            child_contacts = request.env['res.partner'].sudo().search([
                ('parent_id', '=', contact.id),
                ('user_id', '=', request.env.user.id)
            ])
        
        # Pass portal access flags to template for sidebar logic
        return request.render('sales_management_portal.contact_view', {
            'contact': contact,
            'child_contacts': child_contacts,
            'user_has_contact_portal': request.env.user.use_contact_portal,
            'user_has_todo_portal': request.env.user.use_todo_portal,
            'user_has_quotation_portal': request.env.user.use_quotation_portal,
        })

    @http.route('/sales_management/contacts/view-person/<int:contact_id>', type='http', auth='user', website=True)
    def view_contact_person(self, contact_id, **kw):
        """View individual contact person details"""
        # Check portal access
        if not request.env.user.use_contact_portal:
            return request.redirect('/sales_management')
        
        contact = request.env['res.partner'].sudo().browse(contact_id)
        
        # Security check - ensure user can only view their own contacts
        if contact.user_id.id != request.env.user.id:
            return request.redirect('/sales_management/contacts')
        
        # Pass portal access flags to template for sidebar logic
        return request.render('sales_management_portal.contact_person_view', {
            'contact': contact,
            'user_has_contact_portal': request.env.user.use_contact_portal,
            'user_has_todo_portal': request.env.user.use_todo_portal,
            'user_has_quotation_portal': request.env.user.use_quotation_portal,
        })

    @http.route('/sales_management/contacts/get-company-address', type='json', auth='user', website=True)
    def get_company_address(self, company_id, **kw):
        """Get company address for autofill"""
        # Check portal access
        if not request.env.user.use_contact_portal:
            return {}
            
        try:
            company = request.env['res.partner'].sudo().browse(int(company_id))
            return {
                'street': company.street or '',
                'street2': company.street2 or '',
                'city': company.city or '',
                'state_id': company.state_id.id if company.state_id else False,
                'zip': company.zip or '',
                'country_id': company.country_id.id if company.country_id else False,
                'category_id': company.category_id.ids if company.category_id else False,
            }
        except Exception as e:
            _logger.error(f"Error getting company address: {str(e)}")
            return {}

    @http.route('/sales_management/todo', type='http', auth='user', website=True)
    def todo_portal(self, **kw):
        """Todo Portal with enhanced security check"""
        if not request.env.user.use_todo_portal:
            # Redirect to dashboard if no access
            return request.redirect('/sales_management')
        
        # Pass portal access flags to template for sidebar logic
        return request.render('sales_management_portal.todo_portal', {
            'user_has_contact_portal': request.env.user.use_contact_portal,
            'user_has_todo_portal': request.env.user.use_todo_portal,
            'user_has_quotation_portal': request.env.user.use_quotation_portal,
        })

    @http.route('/sales_management/quotation', type='http', auth='user', website=True)
    def quotation_portal(self, **kw):
        """Quotation Portal with enhanced security check"""
        if not request.env.user.use_quotation_portal:
            # Redirect to dashboard if no access
            return request.redirect('/sales_management')
        
        # Pass portal access flags to template for sidebar logic
        return request.render('sales_management_portal.quotation_portal', {
            'user_has_contact_portal': request.env.user.use_contact_portal,
            'user_has_todo_portal': request.env.user.use_todo_portal,
            'user_has_quotation_portal': request.env.user.use_quotation_portal,
        })