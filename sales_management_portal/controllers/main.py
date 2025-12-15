import logging
import json
from odoo import http
from odoo.http import request
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.addons.portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)

class SalesPortalController(CustomerPortal):
    """Sales Management Portal Controller"""

    def _prepare_portal_layout_values(self):
        """Override to add no_footer flag"""
        values = super(SalesPortalController, self)._prepare_portal_layout_values()
        # Add flag to template to hide footer
        values['no_footer'] = True
        return values

    def _has_portal_access(self, user, portal_field):
        """Safely check if user has access to a portal field"""
        try:
            # Use hasattr first to check if field exists
            if hasattr(user, portal_field):
                return getattr(user, portal_field, False)
            return False
        except Exception as e:
            _logger.warning(f"Error checking portal access {portal_field}: {str(e)}")
            return False
    
    def _check_portal_access(self, required_portal):
        """Check if user has access to required portal"""
        user = request.env.user
        try:
            # Check if portal field exists on user
            if not hasattr(user, required_portal):
                _logger.warning(f"Portal field {required_portal} not found on user")
                return False
            
            # Get the field value safely
            return getattr(user, required_portal, False)
        except Exception as e:
            _logger.error(f"Error checking portal access: {str(e)}")
            return False
    
    def _get_portal_access_flags(self):
        """Get all portal access flags safely"""
        user = request.env.user
        portal_fields = [
            'use_contact_portal',
            'use_sales_portal', 
            'use_service_portal',
            'use_quotation_portal'
        ]
        
        portal_access = {}
        for field in portal_fields:
            portal_access[field] = self._has_portal_access(user, field)
        
        return portal_access

    @http.route('/sales_management', type='http', auth='user', website=True)
    def sales_management_home(self, **kw):
        """Sales Management Dashboard Home"""
        # Check if user has access to any portal - SAFE VERSION
        user = request.env.user
        
        # Check each portal field safely
        has_access = False
        portal_fields = [
            'use_contact_portal',
            'use_sales_portal', 
            'use_service_portal',
            'use_quotation_portal'
        ]
        
        for field in portal_fields:
            try:
                if hasattr(user, field) and getattr(user, field, False):
                    has_access = True
                    break
            except Exception:
                continue
        
        if not has_access:
            # Return access denied HTML page instead of redirecting to /web
            html = """
            <html>
            <head>
                <title>Access Denied</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                        margin: 0;
                        padding: 0;
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                    }
                    .access-denied-container {
                        background: white;
                        border-radius: 15px;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                        padding: 40px;
                        text-align: center;
                        max-width: 600px;
                        width: 90%;
                        margin: 20px;
                    }
                    .access-denied-icon {
                        font-size: 80px;
                        color: #ff6b6b;
                        margin-bottom: 20px;
                    }
                    .access-denied-title {
                        color: #dc3545;
                        margin-bottom: 15px;
                        font-size: 28px;
                    }
                    .access-denied-message {
                        color: #495057;
                        font-size: 18px;
                        line-height: 1.6;
                        margin-bottom: 25px;
                    }
                    .portal-badges {
                        display: flex;
                        flex-wrap: wrap;
                        justify-content: center;
                        gap: 10px;
                        margin: 20px 0;
                    }
                    .portal-badge {
                        padding: 8px 16px;
                        border-radius: 20px;
                        font-weight: 600;
                        font-size: 14px;
                    }
                    .badge-sales { background: #007bff; color: white; }
                    .badge-service { background: #28a745; color: white; }
                    .badge-contact { background: #17a2b8; color: white; }
                    .badge-quotation { background: #ffc107; color: #212529; }
                    .contact-admin {
                        margin-top: 25px;
                        padding-top: 20px;
                        border-top: 1px solid #dee2e6;
                        color: #6c757d;
                        font-size: 14px;
                    }
                    @media (max-width: 768px) {
                        .access-denied-container {
                            padding: 25px;
                        }
                        .action-buttons {
                            flex-direction: column;
                        }
                        .btn {
                            width: 100%;
                        }
                    }
                </style>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
            </head>
            <body>
                <div class="access-denied-container">
                    <!-- Icon -->
                    <div class="access-denied-icon">
                        <i class="fas fa-lock"></i>
                    </div>
                    
                    <!-- Title -->
                    <h1 class="access-denied-title">
                        <i class="fas fa-ban"></i> Access Denied
                    </h1>
                    
                    <!-- Message -->
                    <div class="access-denied-message">
                        <p>You don't have access to any portal features.</p>
                        <p>Please contact your administrator to grant you access to one or more portals.</p>
                    </div>
                    
                    <!-- Portal Badges -->
                    <div class="portal-badges">
                        <span class="portal-badge badge-sales">Sales Portal</span>
                        <span class="portal-badge badge-service">Service Portal</span>
                        <span class="portal-badge badge-contact">Contact Portal</span>
                        <span class="portal-badge badge-quotation">Quotation Portal</span>
                    </div>
                    
                    <!-- Contact Admin -->
                    <div class="contact-admin">
                        <p>
                            <i class="fas fa-user-shield"></i>
                            Need access? Please contact your system administrator.
                        </p>
                    </div>
                </div>
                
            </body>
            </html>
            """
            return html
        
        # Get portal access flags
        portal_access = self._get_portal_access_flags()
        values = self._prepare_portal_layout_values()  # This now includes no_footer
        
        # Merge dictionaries properly
        all_values = {**portal_access, **values}
        
        return request.render('sales_management_portal.dashboard_main', all_values)
    
    # --------------------------------------------------------------------
    # SALES PORTAL (ADVANCED FILTER VERSION)
    # --------------------------------------------------------------------
    @http.route(
        ['/sales_management/sales', '/sales_management/sales/page/<int:page>'],
        type='http',
        auth='user',
        website=True,
    )
    def sales_portal(self, page=1, **kw):
        """Advanced Sales Portal With Filters"""
        # Check access safely
        if not self._check_portal_access('use_sales_portal'):
            return request.redirect('/sales_management')

        team = 'sales'
        domain = [
            ('task_team', '=', team),
            ('create_uid', '=', request.env.user.id),
        ]

        search = kw.get('q', '').strip()
        if search:
            domain += [
                '|', '|', '|',
                ('task_title', 'ilike', search),
                ('customer_id.name', 'ilike', search),
                ('company_id.name', 'ilike', search),
                ('remarks', 'ilike', search),
            ]

        date_from = kw.get('date_from', '').strip()
        date_to = kw.get('date_to', '').strip()

        if date_from:
            domain.append(('visit_date', '>=', date_from))
        if date_to:
            domain.append(('visit_date', '<=', date_to))

        customer_id = kw.get('customer_id', '').strip()
        if customer_id.isdigit():
            domain.append(('customer_id', '=', int(customer_id)))

        purpose_id = kw.get('purpose_id', '').strip()
        if purpose_id.isdigit():
            domain.append(('purpose_id', '=', int(purpose_id)))

        Task = request.env['task.management'].sudo()
        tasks = Task.search(domain, limit=20, offset=(page - 1) * 20, order='visit_date desc, id desc')
        task_count = Task.search_count(domain)

        customers = request.env['res.partner'].sudo().search([
            ('id', 'in', Task.search([
                ('task_team', '=', team),
                ('create_uid', '=', request.env.user.id),
            ]).mapped('customer_id').ids)
        ])
        purposes = request.env['task.purpose'].sudo().search([])

        message = kw.get('success') and "🎉 Your Sales Task has been submitted successfully!" or False

        # Get portal access flags and layout values
        portal_access = self._get_portal_access_flags()
        values = self._prepare_portal_layout_values()
        
        # Merge all values
        all_values = {
            'tasks': tasks,
            'task_count': task_count,
            'title': "Sales Tasks",
            'team': team,
            'search': search,
            'date_from': date_from,
            'date_to': date_to,
            'customer_id': customer_id,
            'purpose_id': purpose_id,
            'customers': customers,
            'purposes': purposes,
            'message': message,
            'current_page': page,
            'total_pages': (task_count + 19) // 20,
            **portal_access,
            **values,
        }
        
        return request.render('sales_management_portal.task_list_template', all_values)

    # --------------------------------------------------------------------
    # SERVICE PORTAL (ADVANCED FILTER VERSION)
    # --------------------------------------------------------------------
    @http.route(
        ['/sales_management/service', '/sales_management/service/page/<int:page>'],
        type='http',
        auth='user',
        website=True,
    )
    def service_portal(self, page=1, **kw):
        """Advanced Service Portal With Filters"""
        if not self._check_portal_access('use_service_portal'):
            return request.redirect('/sales_management')

        team = 'service'
        domain = [
            ('task_team', '=', team),
            ('create_uid', '=', request.env.user.id),
        ]

        search = kw.get('q', '').strip()
        if search:
            domain += [
                '|', '|', '|',
                ('task_title', 'ilike', search),
                ('customer_id.name', 'ilike', search),
                ('company_id.name', 'ilike', search),
                ('remarks', 'ilike', search),
            ]

        date_from = kw.get('date_from', '').strip()
        date_to = kw.get('date_to', '').strip()

        if date_from:
            domain.append(('visit_date', '>=', date_from))
        if date_to:
            domain.append(('visit_date', '<=', date_to))

        customer_id = kw.get('customer_id', '').strip()
        if customer_id.isdigit():
            domain.append(('customer_id', '=', int(customer_id)))

        purpose_id = kw.get('purpose_id', '').strip()
        if purpose_id.isdigit():
            domain.append(('purpose_id', '=', int(purpose_id)))

        Task = request.env['task.management'].sudo()
        tasks = Task.search(domain, limit=20, offset=(page - 1) * 20, order='visit_date desc, id desc')
        task_count = Task.search_count(domain)

        customers = request.env['res.partner'].sudo().search([
            ('id', 'in', Task.search([
                ('task_team', '=', team),
                ('create_uid', '=', request.env.user.id),
            ]).mapped('customer_id').ids)
        ])

        purposes = request.env['task.purpose'].sudo().search([])

        message = kw.get('success') and "🎉 Your Service Task has been submitted successfully!" or False

        # Get portal access flags and layout values
        portal_access = self._get_portal_access_flags()
        values = self._prepare_portal_layout_values()
        
        all_values = {
            'tasks': tasks,
            'task_count': task_count,
            'title': "Service Tasks",
            'team': team,
            'search': search,
            'date_from': date_from,
            'date_to': date_to,
            'customer_id': customer_id,
            'purpose_id': purpose_id,
            'customers': customers,
            'purposes': purposes,
            'message': message,
            'current_page': page,
            'total_pages': (task_count + 19) // 20,
            **portal_access,
            **values,
        }
        
        return request.render('sales_management_portal.task_list_template', all_values)

    # --------------------------------------------------------------------
    # VIEW TASK
    # --------------------------------------------------------------------
    @http.route('/sales_management/task/<int:task_id>', type='http', auth='user', website=True)
    def view_task(self, task_id, **kw):
        task = request.env['task.management'].sudo().browse(task_id)
        if not task.exists() or task.create_uid.id != request.env.user.id:
            return request.redirect('/sales_management')

        # Get portal access flags and layout values
        portal_access = self._get_portal_access_flags()
        values = self._prepare_portal_layout_values()
        
        all_values = {
            'task': task,
            **portal_access,
            **values,
        }

        return request.render('sales_management_portal.task_view_template', all_values)

    # --------------------------------------------------------------------
    # VIEW TASK MODAL
    # --------------------------------------------------------------------
    @http.route('/sales_management/task/modal_view/<int:task_id>', type='http', auth='user', website=True)
    def task_modal_view(self, task_id, **kw):
        """Return task details for modal view"""
        try:
            task = request.env['task.management'].sudo().browse(task_id)
            
            # Check if user has access to this task
            if not task.exists() or task.create_uid.id != request.env.user.id:
                return request.render('sales_management_portal.task_modal_view_template', {'task': False})
            
            # Get portal access flags
            portal_access = self._get_portal_access_flags()
            values = self._prepare_portal_layout_values()
            
            all_values = {
                'task': task,
                **portal_access,
                **values,
            }
            
            return request.render('sales_management_portal.task_modal_view_template', all_values)
        except Exception as e:
            logger.error(f"Error loading task modal view: {str(e)}")
            return request.render('sales_management_portal.task_modal_view_template', {'task': False})

    # --------------------------------------------------------------------
    # CREATE TASK
    # --------------------------------------------------------------------
    @http.route('/sales_management/create_task/<string:team>', type='http', auth='user', website=True)
    def create_task(self, team='sales', **kw):
        """Create Task Form - Auto-fill Employee from logged-in user"""
        # Check access safely
        user = request.env.user
        has_sales_access = self._has_portal_access(user, 'use_sales_portal')
        has_service_access = self._has_portal_access(user, 'use_service_portal')
        
        if team == 'sales' and not has_sales_access:
            return request.redirect('/sales_management')
        if team == 'service' and not has_service_access:
            return request.redirect('/sales_management')

        if team not in ('sales', 'service'):
            team = 'sales'

        # Get current user's employee record
        current_employee = request.env['hr.employee'].sudo().search([
            ('user_id', '=', request.env.user.id)
        ], limit=1)
        
        # Get customers (persons only) with parent company info
        customers = request.env['res.partner'].sudo().search([
            ('is_company', '=', False)
        ])
        
        # Get purposes
        purposes = request.env['task.purpose'].sudo().search([])

        # Get portal access flags and layout values
        portal_access = self._get_portal_access_flags()
        values = self._prepare_portal_layout_values()
        
        all_values = {
            'team': team,
            'title': f'Create {team.capitalize()} Task',
            'current_employee': current_employee,
            'customers': customers,
            'purposes': purposes,
            **portal_access,
            **values,
        }
        
        return request.render('sales_management_portal.task_form_template', all_values)
    
    # --------------------------------------------------------------------
    # SUBMIT TASK
    # --------------------------------------------------------------------
    @http.route('/sales_management/submit_task', type='http', auth='user',
            methods=['POST'], website=True, csrf=True)
    def submit_task(self, **kw):

        team = kw.get('team') or 'sales'
        if team not in ('sales', 'service'):
            team = 'sales'

        vals = {
            'task_title': kw.get('task_title'),
            'task_team': team,
        }

        if kw.get('employee_id'):
            vals['employee_id'] = int(kw.get('employee_id'))

        if kw.get('customer_id'):
            vals['customer_id'] = int(kw.get('customer_id'))

        if kw.get('visit_date'):
            vals['visit_date'] = kw.get('visit_date')

        if kw.get('purpose_id'):
            vals['purpose_id'] = int(kw.get('purpose_id'))

        if kw.get('analyzer'):
            vals['analyzer'] = kw.get('analyzer')

        if kw.get('reagents'):
            vals['reagents'] = kw.get('reagents')

        if kw.get('remarks'):
            vals['remarks'] = kw.get('remarks')


        # ✅ SERVICE ONLY
        if team == 'service':
            if kw.get('time_in_dt'):
                vals['time_in_dt'] = kw.get('time_in_dt')

            if kw.get('time_out_dt'):
                vals['time_out_dt'] = kw.get('time_out_dt')

            if kw.get('warranty_type'):
                vals['warranty_type'] = kw.get('warranty_type')

        request.env['task.management'].sudo().create(vals)

        return request.redirect(f'/sales_management/{team}?success=1')
    
    ################Contact Portal########################

    @http.route('/sales_management/contacts', type='http', auth='user', website=True)
    def contacts_dashboard(self, **kw):
        """Contacts List View"""
        # Check portal access
        if not self._check_portal_access('use_contact_portal'):
            return request.redirect('/dashboard')
        
        # Get domain for contacts
        domain = []
        
        # Handle user filter
        user_filter = kw.get('user_filter', '')
        selected_user = None
        if user_filter:
            try:
                user_id = int(user_filter)
                domain.append(('user_id', '=', user_id))
                selected_user = request.env['res.users'].sudo().browse(user_id)
            except (ValueError, Exception):
                pass
        
        # Get contacts with domain
        contacts = request.env['res.partner'].sudo().search(domain)
        
        # Handle search
        search_term = kw.get('search', '')
        if search_term:
            contacts = contacts.filtered(lambda c: 
                search_term.lower() in (c.complete_name or '').lower() or
                search_term.lower() in (c.email or '').lower() or
                search_term.lower() in (c.phone or '').lower() or
                search_term.lower() in (c.city or '').lower() or
                search_term.lower() in (c.state_id.name or '').lower() or
                search_term.lower() in (c.country_id.name or '').lower()
            )
        
        # Get all active users for the filter dropdown
        sales_users = request.env['res.users'].sudo().search([
            # ('active', '=', True),
        ])
        
        message = kw.get('success') and "🎉 Your Contact has been created successfully!" or False

        # Get portal access flags and layout values
        portal_access = self._get_portal_access_flags()
        
        all_values = {
            'contacts': contacts,
            'search_term': search_term,
            'user_filter': user_filter,
            'selected_user': selected_user,
            'sales_users': sales_users,
            'message': message,
            **portal_access,
            'no_footer': True,
        }
        
        return request.render('sales_management_portal.contacts_list', all_values)

    @http.route('/sales_management/contacts/create', type='http', auth='user', website=True)
    def create_contact_form(self, **kw):
        """Display contact creation form"""
        # Check portal access
        if not self._check_portal_access('use_contact_portal'):
            return request.redirect('/sales_management')
        
        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])
        
        # Get portal access flags and layout values
        portal_access = self._get_portal_access_flags()
        values = self._prepare_portal_layout_values()
        
        all_values = {
            'countries': countries,
            'states': states,
            **portal_access,
            **values,
        }
        
        return request.render('sales_management_portal.contact_form', all_values)

    @http.route('/sales_management/contacts/submit', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def submit_contact(self, **kw):
        """Handle contact form submission"""
        try:
            # Check portal access
            if not self._check_portal_access('use_contact_portal'):
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
        if not self._check_portal_access('use_contact_portal'):
            return request.redirect('/sales_management')
        
        contact = request.env['res.partner'].sudo().browse(contact_id)
        
        # Security check - ensure user can only view their own contacts
        # if contact.user_id.id != request.env.user.id:
        #     return request.redirect('/sales_management/contacts')
        
        # Get child contacts for companies
        child_contacts = []
        if contact.is_company:
            child_contacts = request.env['res.partner'].sudo().search([
                ('parent_id', '=', contact.id),
                # ('user_id', '=', request.env.user.id)
            ])
        
        # Get portal access flags and layout values
        portal_access = self._get_portal_access_flags()
        values = self._prepare_portal_layout_values()
        
        all_values = {
            'contact': contact,
            'child_contacts': child_contacts,
            **portal_access,
            **values,
        }
        
        return request.render('sales_management_portal.contact_view', all_values)

    @http.route('/sales_management/contacts/view-person/<int:contact_id>', type='http', auth='user', website=True)
    def view_contact_person(self, contact_id, **kw):
        """View individual contact person details"""
        # Check portal access
        if not self._check_portal_access('use_contact_portal'):
            return request.redirect('/sales_management')
        
        contact = request.env['res.partner'].sudo().browse(contact_id)
        
        # Security check - ensure user can only view their own contacts
        # if contact.user_id.id != request.env.user.id:
        #     return request.redirect('/sales_management/contacts')
        
        # Get portal access flags and layout values
        portal_access = self._get_portal_access_flags()
        values = self._prepare_portal_layout_values()
        
        all_values = {
            'contact': contact,
            **portal_access,
            **values,
        }
        
        return request.render('sales_management_portal.contact_person_view', all_values)

    @http.route('/sales_management/contacts/get-company-address', type='json', auth='user', website=True)
    def get_company_address(self, company_id, **kw):
        """Get company address for autofill"""
        # Check portal access
        if not self._check_portal_access('use_contact_portal'):
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

    ################Search Routes - SIMPLE VERSION########################

    @http.route('/sales_management/search/companies', type='json', auth='user', website=True, methods=['POST'])
    def search_companies(self, **kw):
        """Search companies for dropdown"""
        try:
            search_term = kw.get('search_term', '').strip()
            
            domain = [('is_company', '=', True)]
            
            if search_term:
                domain.append(('name', 'ilike', search_term))
            
            companies = request.env['res.partner'].sudo().search(domain, limit=20, order='name asc')
            
            results = []
            for company in companies:
                results.append({
                    'id': company.id,
                    'name': company.name,
                    'email': company.email or '',
                    'phone': company.phone or '',
                    'type': 'Company'
                })
            
            return {'items': results}
            
        except Exception as e:
            _logger.error(f"Error in company search: {str(e)}")
            return {'items': [], 'error': str(e)}

    @http.route('/sales_management/search/tags', type='json', auth='user', website=True, methods=['POST'])
    def search_tags(self, **kw):
        """Search tags for dropdown"""
        try:
            search_term = kw.get('search_term', '').strip()
            
            domain = []
            if search_term:
                domain.append(('name', 'ilike', search_term))
            
            tags = request.env['res.partner.category'].sudo().search(domain, limit=20, order='name asc')
            
            results = []
            for tag in tags:
                results.append({
                    'id': tag.id,
                    'name': tag.name,
                    'type': 'Tag'
                })
            
            return {'items': results}
            
        except Exception as e:
            _logger.error(f"Error in tag search: {str(e)}")
            return {'items': [], 'error': str(e)}

    @http.route('/sales_management/search/customers', type='json', auth='user', website=True, methods=['POST'])
    def search_customers(self, **kw):
        """Search customers for quotation portal - CORRECTED VERSION"""
        try:
            search_term = kw.get('search_term', '').strip()
            
            domain = []
            
            if search_term:
                domain.append(('name', 'ilike', search_term))
            
            customers = request.env['res.partner'].sudo().search(domain, limit=20, order='name asc')
            
            results = []
            for customer in customers:
                # Get pricelist info
                pricelist_info = ''
                if customer.property_product_pricelist:
                    pricelist_info = customer.property_product_pricelist.name
                
                results.append({
                    'id': customer.id,
                    'name': customer.complete_name,
                    'email': customer.email or '',
                    'phone': customer.phone or '',
                    'pricelist_id': customer.property_product_pricelist.id if customer.property_product_pricelist else False,
                    'pricelist_name': pricelist_info,
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
            
            products = request.env['product.template'].sudo().search(domain, limit=20)
            
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

    @http.route('/sales_management/search/categories', type='json', auth='user', website=True, methods=['POST'])
    def search_categories(self, **kw):
        """Search product categories for quotation portal"""
        try:
            search_term = kw.get('search_term', '').strip()
            
            domain = []
            if search_term:
                domain.append(('name', 'ilike', search_term))
            
            categories = request.env['product.category'].sudo().search(domain, limit=20, order='name asc')
            
            results = []
            for category in categories:
                results.append({
                    'id': category.id,
                    'name': category.name,
                    'type': 'Category'
                })
            
            return {'items': results}
            
        except Exception as e:
            _logger.error(f"Error in category search: {str(e)}")
            return {'items': [], 'error': str(e)}

    @http.route('/sales_management/search/products_by_category', type='json', auth='user', website=True, methods=['POST'])
    def search_products_by_category(self, **kw):
        """Search products filtered by category"""
        try:
            search_term = kw.get('search_term', '').strip()
            category_id = kw.get('category_id', '').strip()
            
            domain = [('sale_ok', '=', True)]
            
            if category_id and category_id.isdigit():
                domain.append(('categ_id', '=', int(category_id)))
            
            if search_term:
                domain.append(('name', 'ilike', search_term))
            
            products = request.env['product.template'].sudo().search(domain, limit=20, order='name asc')
            
            results = []
            for product in products:
                results.append({
                    'id': product.id,
                    'name': product.name,
                    'list_price': product.list_price,
                    'default_code': product.default_code or '',
                    'category_id': product.categ_id.id if product.categ_id else False,
                    'category_name': product.categ_id.name if product.categ_id else '',
                    'type': 'Product'
                })
            
            return {'items': results}
            
        except Exception as e:
            _logger.error(f"Error in product search by category: {str(e)}")
            return {'items': [], 'error': str(e)}

    ################Quotation Portal########################

    @http.route('/sales_management/quotation', type='http', auth='user', website=True)
    def quotation_portal(self, **kw):
        """Quotation Portal with list view"""
        if not self._check_portal_access('use_quotation_portal'):
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
        
        # Handle status filter
        status_filter = kw.get('status_filter', '')
        if status_filter:
            domain.append(('state', '=', status_filter))
        
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
        
        quotations = request.env['sale.order'].sudo().search(domain, order='name DESC')
        
        # Calculate total amount sum
        total_amount_sum = sum(quotations.mapped('amount_total') or [0])
        
        # Status choices for dropdown
        status_choices = [
            ('draft', 'Quotation'),
            ('sent', 'Quotation Sent'),
            ('sale', 'Sales Order'),
            ('cancel', 'Cancelled')
        ]
        
        message = kw.get('success') and "🎉 Your Quotation has been created successfully!" or False
        # Get portal access flags and layout values
        portal_access = self._get_portal_access_flags()
        values = self._prepare_portal_layout_values()
        
        all_values = {
            'quotations': quotations,
            'search_term': search_term,
            'status_filter': status_filter,
            'date_from': date_from,
            'date_to': date_to,
            'total_amount_sum': total_amount_sum,
            'status_choices': status_choices,
            'message': message,
            **portal_access,
            **values,
        }
        
        return request.render('sales_management_portal.quotation_portal', all_values)

    @http.route('/sales_management/quotation/create', type='http', auth='user', website=True)
    def create_quotation_form(self, **kw):
        """Display quotation creation form"""
        if not self._check_portal_access('use_quotation_portal'):
            return request.redirect('/sales_management')
        
        # Get today's date for the form
        today = date.today().strftime('%Y-%m-%d')
        
        # Get portal access flags and layout values
        portal_access = self._get_portal_access_flags()
        values = self._prepare_portal_layout_values()
        
        all_values = {
            'today': today,
            **portal_access,
            **values,
        }
        
        return request.render('sales_management_portal.quotation_form', all_values)

    @http.route('/sales_management/quotation/submit', type='http', auth='user', methods=['POST'], website=True, csrf=True)
    def submit_quotation(self, **kw):
        """Handle quotation form submission - UPDATED WITH CATEGORY"""
        try:
            if not self._check_portal_access('use_quotation_portal'):
                return request.redirect('/sales_management')
            
            current_user_id = request.env.user.id
            
            # Debug: Log all incoming data
            _logger.info("Form submission data received:")
            for key, value in kw.items():
                if isinstance(value, list):
                    _logger.info(f"{key}: {value}")
                else:
                    _logger.info(f"{key}: {value}")
            
            # Validate required fields
            if not kw.get('partner_id'):
                _logger.error("No partner_id provided")
                return request.redirect('/sales_management/quotation/create?error=Please+select+a+customer')
            
            if not kw.get('date_order'):
                _logger.error("No date_order provided")
                return request.redirect('/sales_management/quotation/create?error=Please+select+a+date')
            
            # Create quotation
            quotation_data = {
                'partner_id': int(kw.get('partner_id')),
                'date_order': kw.get('date_order'),
                'user_id': current_user_id,
                'state': 'draft',
            }
            
            # Add pricelist if provided
            if kw.get('pricelist_id'):
                quotation_data['pricelist_id'] = int(kw.get('pricelist_id'))
            
            _logger.info(f"Creating quotation with data: {quotation_data}")
            quotation = request.env['sale.order'].sudo().create(quotation_data)
            _logger.info(f"Quotation created with ID: {quotation.id}")
            
            # Get form data directly from request object
            form_data = request.httprequest.form
            
            # Debug form data structure
            _logger.info(f"Form data: {dict(form_data)}")
            
            # Get lists from form data
            if hasattr(form_data, 'getlist'):
                category_ids = form_data.getlist('category_id[]')
                product_ids = form_data.getlist('product_id[]')
                quantities = form_data.getlist('quantity[]')
                price_units = form_data.getlist('price_unit[]')
            else:
                # Handle as regular dict
                category_ids_raw = kw.get('category_id[]', '')
                product_ids_raw = kw.get('product_id[]', '')
                quantities_raw = kw.get('quantity[]', '')
                price_units_raw = kw.get('price_unit[]', '')
                
                # Split by newline to get list
                category_ids = category_ids_raw.split('\n') if category_ids_raw else []
                product_ids = product_ids_raw.split('\n') if product_ids_raw else []
                quantities = quantities_raw.split('\n') if quantities_raw else []
                price_units = price_units_raw.split('\n') if price_units_raw else []
                
                # Clean up empty strings
                category_ids = [cid.strip() for cid in category_ids if cid.strip()]
                product_ids = [pid.strip() for pid in product_ids if pid.strip()]
                quantities = [q.strip() for q in quantities if q.strip()]
                price_units = [p.strip() for p in price_units if p.strip()]
            
            _logger.info(f"Categories to add: {len(category_ids)} items")
            _logger.info(f"Products to add: {len(product_ids)} items")
            _logger.info(f"Category IDs: {category_ids}")
            _logger.info(f"Product IDs: {product_ids}")
            _logger.info(f"Quantities: {quantities}")
            _logger.info(f"Price Units: {price_units}")
            
            if not product_ids or not any(product_ids):
                _logger.error("No products provided")
                quotation.unlink()
                return request.redirect('/sales_management/quotation/create?error=Please+add+at+least+one+product')
            
            # Create order lines
            order_lines_created = 0
            for i in range(len(product_ids)):
                if product_ids[i] and product_ids[i].strip():
                    try:
                        product_id = int(product_ids[i].strip())
                        quantity = float(quantities[i]) if i < len(quantities) else 1.0
                        price_unit = float(price_units[i]) if i < len(price_units) else 0.0
                        
                        # Get the product
                        product = request.env['product.template'].sudo().browse(product_id)
                        if not product.exists():
                            _logger.error(f"Product ID {product_id} does not exist")
                            continue
                        
                        # Get category for this product line
                        category_id = None
                        if i < len(category_ids) and category_ids[i] and category_ids[i].strip():
                            try:
                                category_id = int(category_ids[i].strip())
                            except ValueError:
                                # If category is invalid, use product's category
                                category_id = product.categ_id.id if product.categ_id else None
                        else:
                            # Use product's category
                            category_id = product.categ_id.id if product.categ_id else None
                        
                        # Prepare order line data
                        order_line_data = {
                            'order_id': quotation.id,
                            'product_id': product_id,
                            'product_uom_qty': quantity,
                            'price_unit': price_unit,
                            'product_uom_id': product.uom_id.id,
                            'name': product.name,
                            'customer_lead': 0.0,
                        }
                        
                        # Add category if available
                        if category_id:
                            order_line_data['product_category_id'] = category_id
                        
                        _logger.info(f"Creating order line with data: {order_line_data}")
                        
                        # Create the order line
                        order_line = request.env['sale.order.line'].sudo().create(order_line_data)
                        order_lines_created += 1
                        
                        _logger.info(f"Order line created successfully: {order_line.id}")
                        
                    except (ValueError, TypeError) as e:
                        _logger.error(f"Error processing product line {i}: {str(e)}")
                        continue
                    except Exception as e:
                        _logger.error(f"Unexpected error creating order line {i}: {str(e)}")
                        continue
            
            _logger.info(f"Total order lines created: {order_lines_created}")
            
            # Check if we created any order lines
            if order_lines_created == 0:
                _logger.error("No order lines were created, deleting quotation")
                quotation.unlink()
                return request.redirect('/sales_management/quotation/create?error=No+valid+products+added')
            
            # Update quotation amounts by triggering recomputation
            quotation.write({})  # This will trigger recomputation of computed fields
            
            # Try to confirm the quotation
            try:
                quotation.action_confirm()
                _logger.info(f"Quotation {quotation.name} confirmed successfully")
            except Exception as e:
                _logger.warning(f"Could not confirm quotation: {str(e)}")
                # Continue anyway, quotation will remain in draft state
            
            # Redirect to success page
            return request.redirect('/sales_management/quotation?success=1&quotation_id=' + str(quotation.id))
            
        except Exception as e:
            _logger.error(f"Error creating quotation: {str(e)}", exc_info=True)
            return request.redirect('/sales_management/quotation/create?error=' + str(e).replace(' ', '+'))

    @http.route('/sales_management/quotation/view/<int:quotation_id>', type='http', auth='user', website=True)
    def view_quotation(self, quotation_id, **kw):
        """View individual quotation details"""
        if not self._check_portal_access('use_quotation_portal'):
            return request.redirect('/sales_management')
        
        quotation = request.env['sale.order'].sudo().browse(quotation_id)
        
        # Security check - ensure user can only view their own quotations
        if quotation.user_id.id != request.env.user.id:
            return request.redirect('/sales_management/quotation')
        
        # Get portal access flags and layout values
        portal_access = self._get_portal_access_flags()
        values = self._prepare_portal_layout_values()
        
        all_values = {
            'quotation': quotation,
            **portal_access,
            **values,
        }
        
        return request.render('sales_management_portal.quotation_view', all_values)

    @http.route('/sales_management/quotation/download_pdf/<int:quotation_id>', type='http', auth='user', website=True)
    def download_quotation_pdf(self, quotation_id, download=True, **kw):
        """
        Direct PDF download for quotations
        Works for both portal and internal users
        """
        if not self._check_portal_access('use_quotation_portal'):
            return request.redirect('/sales_management')
        
        try:
            # Use sudo to bypass access restrictions for PDF generation
            quotation = request.env['sale.order'].sudo().browse(quotation_id)
            
            # Important security check - ensure quotation belongs to current user
            if not quotation.exists() or quotation.user_id.id != request.env.user.id:
                return request.redirect('/sales_management/quotation')
            
            # Generate PDF using report service
            report_service = request.env['ir.actions.report'].sudo()
            
            # Get PDF content
            pdf_content = report_service._render_qweb_pdf(
                'sale.report_saleorder',
                quotation.ids
            )[0]
            
            # Create safe filename
            filename = f"Quotation_{quotation.name.replace('/', '_')}.pdf"
            
            # Return as downloadable response
            response = request.make_response(
                pdf_content,
                headers=[
                    ('Content-Type', 'application/pdf'),
                    ('Content-Disposition', f'attachment; filename="{filename}"'),
                    ('Content-Length', len(pdf_content))
                ]
            )
            
            return response
            
        except Exception as e:
            _logger.error(f"PDF download error for user {request.env.user.id}, quotation {quotation_id}: {str(e)}")
            # Return error message or redirect
            return request.redirect(f'/sales_management/quotation?error=pdf_error')

    @http.route('/sales_management/quotation/get-product-price', type='json', auth='user', website=True)
    def get_product_price(self, product_id, **kw):
        """Get product price for autofill"""
        if not self._check_portal_access('use_quotation_portal'):
            return {'price': 0}
            
        try:
            product = request.env['product.template'].sudo().browse(int(product_id))
            return {
                'price': product.list_price,
                'name': product.name
            }
        except Exception as e:
            _logger.error(f"Error getting product price: {str(e)}")
            return {'price': 0}
    
    @http.route('/sales_management/quotation/get-customer-pricelist', type='json', auth='user', website=True, methods=['POST'])
    def get_customer_pricelist(self, **kw):
        """Get customer's pricelist information"""
        try:
            if not self._check_portal_access('use_quotation_portal'):
                return {'error': 'Access denied'}
            
            customer_id = kw.get('customer_id')
            if not customer_id:
                return {'error': 'No customer ID provided'}
            
            customer = request.env['res.partner'].sudo().browse(int(customer_id))
            if not customer.exists():
                return {'error': 'Customer not found'}
            
            pricelist = customer.property_product_pricelist
            
            if pricelist:
                return {
                    'pricelist_id': pricelist.id,
                    'pricelist_name': pricelist.name,
                    'currency_id': pricelist.currency_id.id if pricelist.currency_id else False,
                    'currency_name': pricelist.currency_id.name if pricelist.currency_id else '',
                    'currency_symbol': pricelist.currency_id.symbol if pricelist.currency_id else '',
                }
            else:
                # Get default pricelist
                default_pricelist = request.env['product.pricelist'].sudo().search([], limit=1)
                if default_pricelist:
                    return {
                        'pricelist_id': default_pricelist.id,
                        'pricelist_name': default_pricelist.name + ' (Default)',
                        'currency_id': default_pricelist.currency_id.id if default_pricelist.currency_id else False,
                        'currency_name': default_pricelist.currency_id.name if default_pricelist.currency_id else '',
                        'currency_symbol': default_pricelist.currency_id.symbol if default_pricelist.currency_id else '',
                    }
                else:
                    return {'error': 'No pricelist found'}
                    
        except Exception as e:
            _logger.error(f"Error getting customer pricelist: {str(e)}")
            return {'error': str(e)}
        
    

    @http.route('/sales_management/quotation/get-product-price-pricelist', type='json', auth='user', website=True, methods=['POST'])
    def get_product_price_pricelist(self, **kw):
        """Get product price from pricelist"""
        try:
            if not self._check_portal_access('use_quotation_portal'):
                return {'price': 0, 'error': 'Access denied'}
            
            product_id = kw.get('product_id')
            pricelist_id = kw.get('pricelist_id')
            quantity = float(kw.get('quantity', 1))
            
            if not product_id or not pricelist_id:
                return {'price': 0, 'error': 'Missing parameters'}
            
            # Get product
            product = request.env['product.template'].sudo().browse(int(product_id))
            if not product.exists():
                return {'price': 0, 'error': 'Product not found'}
            
            # Get pricelist
            pricelist = request.env['product.pricelist'].sudo().browse(int(pricelist_id))
            if not pricelist.exists():
                return {'price': 0, 'error': 'Pricelist not found'}
            
            # Get price from pricelist
            price = pricelist._get_product_price(product, quantity)
            list_price = product.list_price  # Regular price
            
            # Format price
            currency = pricelist.currency_id
            formatted_price = "{:,.2f}".format(price)
            formatted_list_price = "{:,.2f}".format(list_price)
            
            return {
                'price': price,
                'formatted_price': formatted_price,
                'list_price': list_price,
                'formatted_list_price': formatted_list_price,
                'currency_id': currency.id,
                'currency_name': currency.name,
                'currency_symbol': currency.symbol,
                'has_discount': price < list_price,
                'discount_percentage': ((list_price - price) / list_price * 100) if list_price > 0 else 0
            }
            
        except Exception as e:
            _logger.error(f"Error getting product price from pricelist: {str(e)}")
            return {'price': 0, 'error': str(e)}