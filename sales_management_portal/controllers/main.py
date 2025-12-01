import logging
import json
from odoo import http
from odoo.http import request
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT

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
    
    ################Contact Portal########################

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
        
        return request.render('sales_management_portal.contact_form', {
            'countries': countries,
            'states': states,
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

    ################Search Routes - SIMPLE VERSION########################

    @http.route('/sales_management/search/companies', type='json', auth='user', website=True, methods=['POST'])
    def search_companies(self, **kw):
        """Search companies for dropdown - CORRECTED VERSION"""
        try:
            # Log the incoming request
            _logger.info("=== COMPANY SEARCH CALLED ===")
            _logger.info(f"Request data: {kw}")
            
            search_term = kw.get('search_term', '')
            
            domain = [
                ('is_company', '=', True),
            ]
            
            if search_term:
                domain.append(('name', 'ilike', search_term))
            
            companies = request.env['res.partner'].sudo().search(domain, limit=20)
            
            _logger.info(f"Company search - Term: '{search_term}', Found: {len(companies)}")
            
            results = []
            for company in companies:
                results.append({
                    'id': company.id,
                    'name': company.name,
                    'email': company.email or '',
                    'phone': company.phone or '',
                    'type': 'Company'
                })
            
            # Log what we're returning
            _logger.info(f"Returning {len(results)} companies")
            return {'items': results}
            
        except Exception as e:
            _logger.error(f"Error in company search: {str(e)}")
            return {'items': [], 'error': str(e)}

    @http.route('/sales_management/search/tags', type='json', auth='user', website=True, methods=['POST'])
    def search_tags(self, **kw):
        """Search tags for dropdown - CORRECTED VERSION"""
        try:
            _logger.info("=== TAG SEARCH CALLED ===")
            _logger.info(f"Request data: {kw}")
            
            search_term = kw.get('search_term', '')
            
            domain = []
            if search_term:
                domain.append(('name', 'ilike', search_term))
            
            tags = request.env['res.partner.category'].sudo().search(domain, limit=20)
            
            _logger.info(f"Tag search - Term: '{search_term}', Found: {len(tags)}")
            
            results = []
            for tag in tags:
                results.append({
                    'id': tag.id,
                    'name': tag.name,
                    'type': 'Tag'
                })
            
            _logger.info(f"Returning {len(results)} tags")
            return {'items': results}
            
        except Exception as e:
            _logger.error(f"Error in tag search: {str(e)}")
            return {'items': [], 'error': str(e)}

    @http.route('/sales_management/search/customers', type='json', auth='user', website=True, methods=['POST'])
    def search_customers(self, **kw):
        """Search customers for quotation portal - CORRECTED VERSION"""
        try:
            _logger.info("=== CUSTOMER SEARCH CALLED ===")
            _logger.info(f"Request data: {kw}")
            
            search_term = kw.get('search_term', '')
            
            domain = [
                ('is_company', '=', True),
            ]
            
            if search_term:
                domain.append(('name', 'ilike', search_term))
            
            customers = request.env['res.partner'].sudo().search(domain, limit=20)
            
            _logger.info(f"Customer search - Term: '{search_term}', Found: {len(customers)}")
            
            results = []
            for customer in customers:
                results.append({
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email or '',
                    'phone': customer.phone or '',
                    'type': 'Customer'
                })
            
            _logger.info(f"Returning {len(results)} customers")
            return {'items': results}
            
        except Exception as e:
            _logger.error(f"Error in customer search: {str(e)}")
            return {'items': [], 'error': str(e)}

    @http.route('/sales_management/search/products', type='json', auth='user', website=True, methods=['POST'])
    def search_products(self, **kw):
        """Search products for quotation portal - CORRECTED VERSION"""
        try:
            _logger.info("=== PRODUCT SEARCH CALLED ===")
            _logger.info(f"Request data: {kw}")
            
            search_term = kw.get('search_term', '')
            
            domain = [('sale_ok', '=', True)]
            
            if search_term:
                domain.append(('name', 'ilike', search_term))
            
            products = request.env['product.product'].sudo().search(domain, limit=20)
            
            _logger.info(f"Product search - Term: '{search_term}', Found: {len(products)}")
            
            results = []
            for product in products:
                results.append({
                    'id': product.id,
                    'name': product.name,
                    'list_price': product.list_price,
                    'default_code': product.default_code or '',
                    'type': 'Product'
                })
            
            _logger.info(f"Returning {len(results)} products")
            return {'items': results}
            
        except Exception as e:
            _logger.error(f"Error in product search: {str(e)}")
            return {'items': [], 'error': str(e)}

    ################Quotation Portal########################

    @http.route('/sales_management/quotation', type='http', auth='user', website=True)
    def quotation_portal(self, **kw):
        """Quotation Portal with list view"""
        if not request.env.user.use_quotation_portal:
            return request.redirect('/sales_management')
        
        # Get quotations for current user
        user_id = request.env.user.id
        domain = [('user_id', '=', user_id)]
        
        # Handle search
        search_term = kw.get('search', '')
        if search_term:
            domain.extend([
                '|', '|',
                ('name', 'ilike', search_term),
                ('partner_id.name', 'ilike', search_term),
                ('state', 'ilike', search_term)
            ])
        
        # Handle date range filter
        date_from = kw.get('date_from')
        date_to = kw.get('date_to')
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                domain.append(('date_order', '>=', date_from_obj.strftime(DEFAULT_SERVER_DATE_FORMAT)))
            except ValueError:
                pass
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                domain.append(('date_order', '<=', date_to_obj.strftime(DEFAULT_SERVER_DATE_FORMAT)))
            except ValueError:
                pass
        
        quotations = request.env['sale.order'].sudo().search(domain, order='name DESC') #create_date
        
        return request.render('sales_management_portal.quotation_portal', {
            'quotations': quotations,
            'search_term': search_term,
            'date_from': date_from,
            'date_to': date_to,
            'user_has_contact_portal': request.env.user.use_contact_portal,
            'user_has_todo_portal': request.env.user.use_todo_portal,
            'user_has_quotation_portal': request.env.user.use_quotation_portal,
        })

    @http.route('/sales_management/quotation/create', type='http', auth='user', website=True)
    def create_quotation_form(self, **kw):
        """Display quotation creation form"""
        if not request.env.user.use_quotation_portal:
            return request.redirect('/sales_management')
        
        # Get today's date for the form
        today = date.today().strftime('%Y-%m-%d')
        
        return request.render('sales_management_portal.quotation_form', {
            'today': today,
            'user_has_contact_portal': request.env.user.use_contact_portal,
            'user_has_todo_portal': request.env.user.use_todo_portal,
            'user_has_quotation_portal': request.env.user.use_quotation_portal,
        })

    @http.route('/sales_management/quotation/submit', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def submit_quotation(self, **kw):
        """Handle quotation form submission"""
        try:
            if not request.env.user.use_quotation_portal:
                return request.redirect('/sales_management')
            
            current_user_id = request.env.user.id
            
            # Create quotation
            quotation_data = {
                'partner_id': int(kw.get('partner_id')),
                'date_order': kw.get('date_order'),
                'user_id': current_user_id,
            }
            
            quotation = request.env['sale.order'].sudo().create(quotation_data)
            
            # Handle order lines
            product_ids = kw.getlist('product_id[]')
            quantities = kw.getlist('quantity[]')
            
            for i in range(len(product_ids)):
                if product_ids[i] and quantities[i]:
                    # Use product.product directly
                    product = request.env['product.product'].sudo().browse(int(product_ids[i]))
                    order_line_data = {
                        'order_id': quotation.id,
                        'product_id': product.id,
                        'product_uom_qty': float(quantities[i]),
                        'price_unit': product.list_price,
                    }
                    request.env['sale.order.line'].sudo().create(order_line_data)
            
            # Confirm quotation
            quotation.action_confirm()
            
            return request.redirect('/sales_management/quotation?success=1')
            
        except Exception as e:
            _logger.error(f"Error creating quotation: {str(e)}")
            return request.redirect('/sales_management/quotation/create?error=1')

    @http.route('/sales_management/quotation/view/<int:quotation_id>', type='http', auth='user', website=True)
    def view_quotation(self, quotation_id, **kw):
        """View individual quotation details"""
        if not request.env.user.use_quotation_portal:
            return request.redirect('/sales_management')
        
        quotation = request.env['sale.order'].sudo().browse(quotation_id)
        
        # Security check - ensure user can only view their own quotations
        if quotation.user_id.id != request.env.user.id:
            return request.redirect('/sales_management/quotation')
        
        return request.render('sales_management_portal.quotation_view', {
            'quotation': quotation,
            'user_has_contact_portal': request.env.user.use_contact_portal,
            'user_has_todo_portal': request.env.user.use_todo_portal,
            'user_has_quotation_portal': request.env.user.use_quotation_portal,
        })

    @http.route('/sales_management/quotation/print/<int:quotation_id>', type='http', auth='user', website=True)
    def print_quotation(self, quotation_id, **kw):
        """Print quotation PDF - Final working solution"""
        if not request.env.user.use_quotation_portal:
            return request.redirect('/sales_management')
        
        quotation = request.env['sale.order'].sudo().browse(quotation_id)
        
        # Security check
        if quotation.user_id.id != request.env.user.id:
            return request.redirect('/sales_management/quotation')
        
        # Use Odoo's built-in report URL - this is the most reliable method
        report_url = f'/report/pdf/sale.report_saleorder/{quotation_id}'
        return request.redirect(report_url)

    @http.route('/sales_management/quotation/get-product-price', type='json', auth='user', website=True)
    def get_product_price(self, product_id, **kw):
        """Get product price for autofill"""
        if not request.env.user.use_quotation_portal:
            return {'price': 0}
            
        try:
            product = request.env['product.product'].sudo().browse(int(product_id))
            return {
                'price': product.list_price,
                'name': product.name
            }
        except Exception as e:
            _logger.error(f"Error getting product price: {str(e)}")
            return {'price': 0}
        

    @http.route('/sales_management/search/debug', type='http', auth='user', website=True)
    def search_debug(self, **kw):
        """Debug endpoint to check data"""
        companies = request.env['res.partner'].sudo().search([('is_company', '=', True)])
        tags = request.env['res.partner.category'].sudo().search([])
        products = request.env['product.product'].sudo().search([('sale_ok', '=', True)])
        
        result = f"""
        <h3>Debug Data</h3>
        <p>Total Companies: {len(companies)}</p>
        <ul>
            {''.join([f'<li>{c.name} (ID: {c.id})</li>' for c in companies])}
        </ul>
        
        <p>Total Tags: {len(tags)}</p>
        <ul>
            {''.join([f'<li>{t.name} (ID: {t.id})</li>' for t in tags])}
        </ul>
        
        <p>Total Products: {len(products)}</p>
        <ul>
            {''.join([f'<li>{p.name} (ID: {p.id})</li>' for p in products[:10]])}
        </ul>
        """
        
        return result
    


    @http.route('/sales_management/search/test', type='json', auth='user', website=True, methods=['POST'])
    def search_test(self, **kw):
        """Test endpoint to debug search"""
        _logger.info("=== SEARCH TEST CALLED ===")
        _logger.info(f"Request data: {kw}")
        
        search_term = kw.get('search_term', '')
        
        # Test companies
        companies = request.env['res.partner'].sudo().search([('is_company', '=', True)], limit=5)
        _logger.info(f"Found {len(companies)} companies")
        
        results = []
        for company in companies:
            results.append({
                'id': company.id,
                'name': company.name,
                'email': company.email or '',
                'phone': company.phone or '',
                'type': 'Company'
            })
        
        _logger.info(f"Returning results: {results}")
        return {'items': results}