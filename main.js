/*
==============================================
ATTENDANCE SYSTEM - MAIN JAVASCRIPT FILE
==============================================
This file contains common JavaScript functions
used across multiple pages.
*/

// ==============================================
// 1. UTILITY FUNCTIONS
// ==============================================

/**
 * Format date to YYYY-MM-DD format
 * @param {Date} date - Date object
 * @returns {string} Formatted date string
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * Format time to HH:MM:SS format
 * @param {Date} date - Date object
 * @returns {string} Formatted time string
 */
function formatTime(date) {
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
}

/**
 * Get today's date in YYYY-MM-DD format
 * @returns {string} Today's date
 */
function getTodayDate() {
    return formatDate(new Date());
}

/**
 * Get current time in HH:MM:SS format
 * @returns {string} Current time
 */
function getCurrentTime() {
    return formatTime(new Date());
}

/**
 * Calculate date N days ago
 * @param {number} days - Number of days to subtract
 * @returns {string} Date string
 */
function getDaysAgo(days) {
    const date = new Date();
    date.setDate(date.getDate() - days);
    return formatDate(date);
}

// ==============================================
// 2. API HELPER FUNCTIONS
// ==============================================

/**
 * Make API call with error handling
 * @param {string} url - API endpoint
 * @param {object} options - Fetch options
 * @returns {Promise} API response
 */
async function apiCall(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('API Error:', error);
        return {
            success: false,
            message: 'Network error. Please check your connection.'
        };
    }
}

/**
 * Show notification toast
 * @param {string} message - Message to display
 * @param {string} type - Type: success, error, info, warning
 */
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    
    // Add styles
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.padding = '15px 25px';
    toast.style.borderRadius = '8px';
    toast.style.zIndex = '9999';
    toast.style.animation = 'slideIn 0.3s ease';
    toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    toast.style.fontWeight = '500';
    
    // Set colors based on type
    const colors = {
        success: { bg: '#d4edda', color: '#155724', border: '#c3e6cb' },
        error: { bg: '#f8d7da', color: '#721c24', border: '#f5c6cb' },
        info: { bg: '#d1ecf1', color: '#0c5460', border: '#bee5eb' },
        warning: { bg: '#fff3cd', color: '#856404', border: '#ffeeba' }
    };
    
    const style = colors[type] || colors.info;
    toast.style.background = style.bg;
    toast.style.color = style.color;
    toast.style.border = `1px solid ${style.border}`;
    
    // Add to page
    document.body.appendChild(toast);
    
    // Remove after 3 seconds
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Add animation styles
if (!document.getElementById('toast-animations')) {
    const style = document.createElement('style');
    style.id = 'toast-animations';
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// ==============================================
// 3. FORM VALIDATION
// ==============================================

/**
 * Validate email format
 * @param {string} email - Email address
 * @returns {boolean} True if valid
 */
function isValidEmail(email) {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
}

/**
 * Validate phone number (Indian format)
 * @param {string} phone - Phone number
 * @returns {boolean} True if valid
 */
function isValidPhone(phone) {
    const regex = /^[6-9]\d{9}$/;
    return regex.test(phone.replace(/\s/g, ''));
}

/**
 * Validate required fields in form
 * @param {HTMLFormElement} form - Form element
 * @returns {boolean} True if all required fields are filled
 */
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#dc3545';
            isValid = false;
        } else {
            field.style.borderColor = '#ddd';
        }
    });
    
    if (!isValid) {
        showToast('Please fill all required fields', 'error');
    }
    
    return isValid;
}

// ==============================================
// 4. LOCAL STORAGE HELPERS
// ==============================================

/**
 * Save data to localStorage
 * @param {string} key - Storage key
 * @param {any} value - Value to store
 */
function saveToLocalStorage(key, value) {
    try {
        localStorage.setItem(key, JSON.stringify(value));
    } catch (error) {
        console.error('LocalStorage save error:', error);
    }
}

/**
 * Load data from localStorage
 * @param {string} key - Storage key
 * @returns {any} Stored value or null
 */
function loadFromLocalStorage(key) {
    try {
        const value = localStorage.getItem(key);
        return value ? JSON.parse(value) : null;
    } catch (error) {
        console.error('LocalStorage load error:', error);
        return null;
    }
}

/**
 * Remove data from localStorage
 * @param {string} key - Storage key
 */
function removeFromLocalStorage(key) {
    try {
        localStorage.removeItem(key);
    } catch (error) {
        console.error('LocalStorage remove error:', error);
    }
}

// ==============================================
// 5. IMAGE PROCESSING
// ==============================================

/**
 * Compress image before upload
 * @param {File} file - Image file
 * @param {number} maxWidth - Maximum width
 * @param {number} quality - JPEG quality (0-1)
 * @returns {Promise<string>} Base64 compressed image
 */
function compressImage(file, maxWidth = 800, quality = 0.8) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const img = new Image();
            
            img.onload = function() {
                const canvas = document.createElement('canvas');
                let width = img.width;
                let height = img.height;
                
                // Calculate new dimensions
                if (width > maxWidth) {
                    height = (height * maxWidth) / width;
                    width = maxWidth;
                }
                
                canvas.width = width;
                canvas.height = height;
                
                const ctx = canvas.getContext('2d');
                ctx.drawImage(img, 0, 0, width, height);
                
                // Convert to base64
                const compressedImage = canvas.toDataURL('image/jpeg', quality);
                resolve(compressedImage);
            };
            
            img.onerror = reject;
            img.src = e.target.result;
        };
        
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

/**
 * Convert base64 to Blob
 * @param {string} base64 - Base64 string
 * @returns {Blob} Blob object
 */
function base64ToBlob(base64) {
    const parts = base64.split(';base64,');
    const contentType = parts[0].split(':')[1];
    const raw = window.atob(parts[1]);
    const rawLength = raw.length;
    const uInt8Array = new Uint8Array(rawLength);
    
    for (let i = 0; i < rawLength; ++i) {
        uInt8Array[i] = raw.charCodeAt(i);
    }
    
    return new Blob([uInt8Array], { type: contentType });
}

// ==============================================
// 6. TABLE UTILITIES
// ==============================================

/**
 * Export table to CSV
 * @param {HTMLTableElement} table - Table element
 * @param {string} filename - Output filename
 */
function exportTableToCSV(table, filename = 'data.csv') {
    let csv = [];
    const rows = table.querySelectorAll('tr');
    
    for (let i = 0; i < rows.length; i++) {
        const row = [];
        const cols = rows[i].querySelectorAll('td, th');
        
        for (let j = 0; j < cols.length; j++) {
            // Clean the text and escape quotes
            let data = cols[j].innerText.replace(/(\r\n|\n|\r)/gm, '').replace(/(\s\s)/gm, ' ');
            data = data.replace(/"/g, '""');
            row.push('"' + data + '"');
        }
        
        csv.push(row.join(','));
    }
    
    // Create download link
    const csvString = csv.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', filename);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

/**
 * Filter table rows by search term
 * @param {HTMLTableElement} table - Table element
 * @param {string} searchTerm - Search term
 */
function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    const term = searchTerm.toLowerCase();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(term) ? '' : 'none';
    });
}

/**
 * Sort table by column
 * @param {HTMLTableElement} table - Table element
 * @param {number} columnIndex - Column index to sort by
 * @param {boolean} ascending - Sort direction
 */
function sortTableByColumn(table, columnIndex, ascending = true) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();
        
        // Check if values are numbers
        const aNum = parseFloat(aValue);
        const bNum = parseFloat(bValue);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return ascending ? aNum - bNum : bNum - aNum;
        }
        
        // String comparison
        return ascending ? 
            aValue.localeCompare(bValue) : 
            bValue.localeCompare(aValue);
    });
    
    // Re-append sorted rows
    rows.forEach(row => tbody.appendChild(row));
}

// ==============================================
// 7. LOADING INDICATOR
// ==============================================

/**
 * Show loading spinner
 * @param {string} message - Loading message
 */
function showLoading(message = 'Loading...') {
    // Check if loader already exists
    let loader = document.getElementById('global-loader');
    
    if (!loader) {
        loader = document.createElement('div');
        loader.id = 'global-loader';
        loader.innerHTML = `
            <div class="loader-overlay">
                <div class="loader-content">
                    <div class="spinner"></div>
                    <p class="loader-text">${message}</p>
                </div>
            </div>
        `;
        
        // Add styles
        const style = document.createElement('style');
        style.textContent = `
            .loader-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            }
            
            .loader-content {
                background: white;
                padding: 40px;
                border-radius: 12px;
                text-align: center;
            }
            
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 50px;
                height: 50px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .loader-text {
                color: #333;
                font-size: 16px;
                margin: 0;
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(loader);
    }
}

/**
 * Hide loading spinner
 */
function hideLoading() {
    const loader = document.getElementById('global-loader');
    if (loader) {
        loader.remove();
    }
}

// ==============================================
// 8. CONFIRMATION DIALOG
// ==============================================

/**
 * Show custom confirmation dialog
 * @param {string} message - Confirmation message
 * @param {Function} onConfirm - Callback on confirm
 * @param {Function} onCancel - Callback on cancel
 */
function showConfirmDialog(message, onConfirm, onCancel) {
    const dialog = document.createElement('div');
    dialog.className = 'custom-dialog';
    dialog.innerHTML = `
        <div class="dialog-overlay">
            <div class="dialog-content">
                <h3>Confirm Action</h3>
                <p>${message}</p>
                <div class="dialog-buttons">
                    <button class="btn btn-success" id="confirm-btn">Yes</button>
                    <button class="btn btn-secondary" id="cancel-btn">No</button>
                </div>
            </div>
        </div>
    `;
    
    // Add styles
    const style = document.createElement('style');
    style.textContent = `
        .dialog-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
        }
        
        .dialog-content {
            background: white;
            padding: 30px;
            border-radius: 12px;
            max-width: 400px;
            text-align: center;
        }
        
        .dialog-content h3 {
            color: #333;
            margin-bottom: 15px;
        }
        
        .dialog-content p {
            color: #666;
            margin-bottom: 25px;
        }
        
        .dialog-buttons {
            display: flex;
            gap: 15px;
            justify-content: center;
        }
    `;
    
    document.head.appendChild(style);
    document.body.appendChild(dialog);
    
    // Event listeners
    document.getElementById('confirm-btn').onclick = function() {
        document.body.removeChild(dialog);
        if (onConfirm) onConfirm();
    };
    
    document.getElementById('cancel-btn').onclick = function() {
        document.body.removeChild(dialog);
        if (onCancel) onCancel();
    };
}

// ==============================================
// 9. DEBOUNCE FUNCTION
// ==============================================

/**
 * Debounce function to limit API calls
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in ms
 * @returns {Function} Debounced function
 */
function debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ==============================================
// 10. BROWSER DETECTION
// ==============================================

/**
 * Check if browser supports required features
 * @returns {object} Support status
 */
function checkBrowserSupport() {
    return {
        camera: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
        localStorage: typeof(Storage) !== "undefined",
        canvas: !!document.createElement('canvas').getContext,
        fileReader: typeof FileReader !== 'undefined'
    };
}

/**
 * Show browser compatibility warning if needed
 */
function checkCompatibility() {
    const support = checkBrowserSupport();
    const missing = [];
    
    if (!support.camera) missing.push('Camera Access');
    if (!support.localStorage) missing.push('Local Storage');
    if (!support.canvas) missing.push('Canvas');
    if (!support.fileReader) missing.push('File Reader');
    
    if (missing.length > 0) {
        showToast(
            `Your browser doesn't support: ${missing.join(', ')}. Please use a modern browser.`,
            'warning'
        );
    }
}

// ==============================================
// 11. INITIALIZATION
// ==============================================

/**
 * Initialize common functionality when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check browser compatibility
    // checkCompatibility();
    
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Auto-focus first input in forms
    const firstInput = document.querySelector('input:not([type="hidden"])');
    if (firstInput) {
        firstInput.focus();
    }
});

// ==============================================
// 12. EXPORT FOR USE IN OTHER FILES
// ==============================================

// Make functions available globally
window.attendanceSystem = {
    formatDate,
    formatTime,
    getTodayDate,
    getCurrentTime,
    getDaysAgo,
    apiCall,
    showToast,
    isValidEmail,
    isValidPhone,
    validateForm,
    saveToLocalStorage,
    loadFromLocalStorage,
    removeFromLocalStorage,
    compressImage,
    base64ToBlob,
    exportTableToCSV,
    filterTable,
    sortTableByColumn,
    showLoading,
    hideLoading,
    showConfirmDialog,
    debounce,
    checkBrowserSupport
};

// Console message
console.log('%c✅ Attendance System Loaded', 'color: #667eea; font-size: 16px; font-weight: bold');
console.log('%cMain JavaScript utilities are ready to use', 'color: #666; font-size: 12px');