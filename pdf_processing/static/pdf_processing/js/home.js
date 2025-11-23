// Home page JavaScript

const API_BASE = '/api/pdf';

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeUploadForm();
    initializeDragAndDrop();
    initializeFileDisplay();
    loadDocuments();
    setupRefreshButton();
});

/**
 * Initialize drag and drop functionality
 */
function initializeDragAndDrop() {
    const fileInput = document.getElementById('pdf-file');
    const fileDisplay = document.getElementById('file-display');
    const wrapper = fileInput?.closest('.file-upload-wrapper');
    
    if (!wrapper || !fileDisplay) return;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        wrapper.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop area when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        wrapper.addEventListener(eventName, () => {
            wrapper.classList.add('dragover');
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        wrapper.addEventListener(eventName, () => {
            wrapper.classList.remove('dragover');
        }, false);
    });
    
    // Handle dropped files
    wrapper.addEventListener('drop', handleDrop, false);
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            updateFileDisplay(files[0]);
        }
    }
}

/**
 * Initialize file display updates
 */
function initializeFileDisplay() {
    const fileInput = document.getElementById('pdf-file');
    const fileDisplay = document.getElementById('file-display');
    
    if (!fileInput || !fileDisplay) return;
    
    fileInput.addEventListener('change', function() {
        if (this.files && this.files[0]) {
            updateFileDisplay(this.files[0]);
        }
    });
}

/**
 * Update file display when file is selected
 */
function updateFileDisplay(file) {
    const fileDisplay = document.getElementById('file-display');
    if (!fileDisplay) return;
    
    fileDisplay.classList.add('has-file');
    
    const textElement = fileDisplay.querySelector('.file-upload-text');
    const hintElement = fileDisplay.querySelector('.file-upload-hint');
    
    if (textElement) {
        textElement.textContent = `Selected: ${file.name}`;
    }
    
    if (hintElement) {
        // Store original text if not already stored
        if (!hintElement.dataset.originalText) {
            hintElement.dataset.originalText = hintElement.textContent;
        }
        hintElement.textContent = `Size: ${formatFileSize(file.size)}`;
    }
}

/**
 * Initialize upload form
 */
function initializeUploadForm() {
    const form = document.getElementById('upload-form');
    const uploadBtn = document.getElementById('upload-btn');
    const uploadMessage = document.getElementById('upload-message');
    
    if (!form) return;
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const fileInput = document.getElementById('pdf-file');
        const titleInput = document.getElementById('document-title');
        const file = fileInput.files[0];
        
        if (!file) {
            showUploadMessage('⚠️ Please select a PDF file', 'error');
            return;
        }
        
        // Validate file type
        if (!file.name.toLowerCase().endsWith('.pdf')) {
            showUploadMessage('❌ Only PDF files are allowed', 'error');
            return;
        }
        
        // Disable form during upload
        uploadBtn.disabled = true;
        uploadBtn.querySelector('.btn-text').style.display = 'none';
        uploadBtn.querySelector('.btn-spinner').style.display = 'inline';
        uploadMessage.style.display = 'none';
        
        // Create form data
        const formData = new FormData();
        formData.append('file', file);
        if (titleInput.value.trim()) {
            formData.append('title', titleInput.value.trim());
        }
        
        try {
            const response = await fetch(`${API_BASE}/upload/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (response.ok) {
                showUploadMessage('✅ PDF uploaded successfully! Processing started...', 'success');
                form.reset();
                
                // Reset file display
                const fileDisplay = document.getElementById('file-display');
                if (fileDisplay) {
                    fileDisplay.classList.remove('has-file');
                    const textElement = fileDisplay.querySelector('.file-upload-text');
                    const hintElement = fileDisplay.querySelector('.file-upload-hint');
                    if (textElement) {
                        textElement.textContent = 'Click to browse or drag and drop PDF file here';
                    }
                    if (hintElement) {
                        // Restore original hint text from the initial page load
                        hintElement.textContent = hintElement.dataset.originalText || 'Maximum file size: 10MB';
                    }
                }
                
                // Reload documents after a short delay
                setTimeout(() => {
                    loadDocuments();
                    // Redirect to document detail page
                    window.location.href = `/document/${data.document_id}/`;
                }, 1000);
            } else {
                showUploadMessage('❌ ' + (data.error || 'Upload failed'), 'error');
            }
        } catch (error) {
            console.error('Upload error:', error);
            showUploadMessage('An error occurred during upload', 'error');
        } finally {
            // Re-enable form
            uploadBtn.disabled = false;
            uploadBtn.querySelector('.btn-text').style.display = 'inline';
            uploadBtn.querySelector('.btn-spinner').style.display = 'none';
        }
    });
}

/**
 * Show upload message
 */
function showUploadMessage(message, type) {
    const uploadMessage = document.getElementById('upload-message');
    if (!uploadMessage) return;
    
    uploadMessage.textContent = message;
    uploadMessage.className = `upload-message ${type}`;
    uploadMessage.style.display = 'block';
    
    // Auto-hide after 5 seconds for success messages
    if (type === 'success') {
        setTimeout(() => {
            uploadMessage.style.display = 'none';
        }, 5000);
    }
}

/**
 * Load documents list
 */
async function loadDocuments() {
    const container = document.getElementById('documents-container');
    if (!container) return;
    
    container.innerHTML = '<div class="documents-loading">Loading documents...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/documents/`);
        const data = await response.json();
        
        if (response.ok && data.documents) {
            displayDocuments(data.documents);
        } else {
            container.innerHTML = '<div class="documents-empty">Failed to load documents</div>';
        }
    } catch (error) {
        console.error('Error loading documents:', error);
        container.innerHTML = '<div class="documents-empty">Error loading documents. Please try again.</div>';
    }
}

/**
 * Display documents in the container
 */
function displayDocuments(documents) {
    const container = document.getElementById('documents-container');
    if (!container) return;
    
    if (documents.length === 0) {
        container.innerHTML = '<div class="documents-empty">No documents yet. Upload your first PDF to get started!</div>';
        return;
    }
    
    container.innerHTML = documents.map(doc => createDocumentCard(doc)).join('');
    
    // Add click handlers for document cards
    container.querySelectorAll('.document-card').forEach(card => {
        card.addEventListener('click', function(e) {
            // Don't navigate if clicking on action buttons
            if (e.target.closest('.document-card-actions')) {
                return;
            }
            const documentId = this.dataset.documentId;
            window.location.href = `/document/${documentId}/`;
        });
    });
    
    // Add delete button handlers
    container.querySelectorAll('.delete-btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            const documentId = this.dataset.documentId;
            deleteDocument(documentId);
        });
    });
}

/**
 * Create document card HTML
 */
function createDocumentCard(doc) {
    const statusClass = `status-${doc.processing_status}`;
    const statusText = doc.processing_status.charAt(0).toUpperCase() + doc.processing_status.slice(1);
    
    return `
        <div class="document-card" data-document-id="${doc.document_id}">
            <div class="document-card-content">
                <div class="document-card-title">${escapeHtml(doc.title)}</div>
                <div class="document-card-meta">
                    <span class="status-badge ${statusClass}">${statusText}</span>
                    <span>${formatFileSize(doc.file_size || 0)}</span>
                    ${doc.page_count ? `<span>${doc.page_count} pages</span>` : ''}
                    <span>${formatDate(doc.upload_date)}</span>
                </div>
            </div>
            <div class="document-card-actions">
                <button class="btn btn-danger btn-small delete-btn" data-document-id="${doc.document_id}">
                    Delete
                </button>
            </div>
        </div>
    `;
}

/**
 * Delete document
 */
async function deleteDocument(documentId) {
    if (!confirm('Are you sure you want to delete this document? This action cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/documents/${documentId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showAlert('Document deleted successfully', 'success');
            loadDocuments();
        } else {
            showAlert(data.error || 'Failed to delete document', 'error');
        }
    } catch (error) {
        console.error('Delete error:', error);
        showAlert('An error occurred while deleting the document', 'error');
    }
}

/**
 * Setup refresh button
 */
function setupRefreshButton() {
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            this.disabled = true;
            this.textContent = '🔄 Refreshing...';
            loadDocuments().finally(() => {
                this.disabled = false;
                this.textContent = '🔄 Refresh';
            });
        });
    }
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

