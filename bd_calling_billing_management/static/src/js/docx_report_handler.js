// static/src/js/docx_rename.js
/** @odoo-module **/

import { registry } from "@web/core/registry";

// Monkey-patch the download function
const originalDownload = window.download;

window.download = function(data, options) {
    // Check if this is a DOCX report
    if (options && options.url && options.url.includes('docx')) {
        // Create a custom download that renames the file
        fetch(options.url)
            .then(response => response.blob())
            .then(blob => {
                // Extract filename from URL or use default
                let filename = 'document.docx';
                const urlParts = options.url.split('/');
                if (urlParts.length > 0) {
                    const lastPart = urlParts[urlParts.length - 1];
                    if (lastPart.includes('.pdf')) {
                        filename = lastPart.replace('.pdf', '.docx');
                    }
                }
                
                // Create download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            });
        return;
    }
    
    // Use original download for other files
    return originalDownload.apply(this, arguments);
};

// Register our handler
registry.category("ir.actions.report handlers").add("docx_rename_handler", async function(action, options, env) {
    if (action.name && action.name.includes('DOCX')) {
        // Let Odoo handle it normally, our monkey-patch will rename it
        return false;
    }
    return false;
});