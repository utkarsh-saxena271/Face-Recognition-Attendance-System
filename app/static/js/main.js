// ============================================
// MODERN FACE RECOGNITION ATTENDANCE - MAIN JS
// ============================================

let videoStream = null;

function getCameraSupportError() {
    if (!navigator.mediaDevices || typeof navigator.mediaDevices.getUserMedia !== 'function') {
        if (!window.isSecureContext && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
            return 'Camera access requires HTTPS or localhost in this browser. Open the app with a secure URL.';
        }

        return 'This browser does not support camera access here. Please use a recent Chrome, Edge, or Safari browser.';
    }

    return null;
}

/**
 * Start camera and request permissions
 */
async function startCamera(videoElementId) {
    const video = document.getElementById(videoElementId);

    if (!video) {
        console.warn('Camera video element not found:', videoElementId);
        return;
    }

    const cameraSupportError = getCameraSupportError();
    if (cameraSupportError) {
        notifyError(cameraSupportError, 7000);
        return;
    }

    try {
        const preferredConstraints = {
            video: {
                facingMode: { ideal: 'user' },
                width: { ideal: 1280 },
                height: { ideal: 960 }
            },
            audio: false
        };
        const fallbackConstraints = {
            video: true,
            audio: false
        };

        try {
            videoStream = await navigator.mediaDevices.getUserMedia(preferredConstraints);
        } catch (constraintError) {
            console.warn('Falling back to basic camera constraints:', constraintError);
            videoStream = await navigator.mediaDevices.getUserMedia(fallbackConstraints);
        }

        video.srcObject = videoStream;
        await video.play().catch(() => {});
        console.log('Camera started successfully');
    } catch (err) {
        console.error('Camera error:', err);
        if (err.name === 'NotAllowedError') {
            notifyError('Camera permission denied. Please allow camera access in your browser settings.');
        } else if (err.name === 'NotFoundError') {
            notifyError('No camera found. Please connect a camera to your device.');
        } else {
            notifyError('Could not access the camera. Error: ' + err.message);
        }
    }
}

/**
 * Stop video stream
 */
function stopCamera() {
    if (videoStream) {
        videoStream.getTracks().forEach(track => track.stop());
        videoStream = null;
    }
}

/**
 * Capture frame and convert to base64
 */
function captureBase64(videoElementId, canvasElementId) {
    const video = document.getElementById(videoElementId);
    const canvas = document.getElementById(canvasElementId);

    const cameraSupportError = getCameraSupportError();
    if (cameraSupportError) {
        throw new Error(cameraSupportError);
    }

    const context = canvas.getContext('2d');

    if (!video.videoWidth || !video.videoHeight) {
        throw new Error('Camera is still loading. Please wait a moment and try again.');
    }
    
    // Setup canvas size to match video
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    
    // Draw current frame
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Get base64 (JPEG for smaller file size)
    return canvas.toDataURL('image/jpeg', 0.85);
}

/**
 * Show toast notification for success
 */
function notifySuccess(message, duration = 4000) {
    showToast(message, 'success', duration);
}

/**
 * Show toast notification for error
 */
function notifyError(message, duration = 4000) {
    showToast(message, 'error', duration);
}

/**
 * Show toast notification for warning
 */
function notifyWarning(message, duration = 4000) {
    showToast(message, 'warning', duration);
}

/**
 * Show toast notification for info
 */
function notifyInfo(message, duration = 4000) {
    showToast(message, 'info', duration);
}

/**
 * Generic toast notification system
 */
function showToast(message, type = 'info', duration = 4000) {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    // Create toast element
    const toastId = 'toast-' + Date.now();
    const Toast = window.bootstrap?.Toast;

    const toastHTML = `
        <div id="${toastId}" class="toast ${type}" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header">
                <div class="d-flex align-items-center">
                    <i class="bi bi-${getIconByType(type)} me-2 fs-5" style="color: ${getColorByType(type)};"></i>
                    <strong class="me-auto">${getHeaderByType(type)}</strong>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${escapeHtml(message)}
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = document.getElementById(toastId);

    if (Toast) {
        const toast = new Toast(toastElement);
        toast.show();

        // Auto remove after duration
        setTimeout(() => {
            toastElement.remove();
        }, duration + 300);
    } else {
        // Fallback if Bootstrap is not available
        setTimeout(() => {
            toastElement.remove();
        }, duration);
    }
}

/**
 * Get icon based on notification type
 */
function getIconByType(type) {
    const icons = {
        success: 'check-circle-fill',
        error: 'exclamation-circle-fill',
        warning: 'exclamation-triangle-fill',
        info: 'info-circle-fill'
    };
    return icons[type] || 'info-circle-fill';
}

/**
 * Get color based on notification type
 */
function getColorByType(type) {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    return colors[type] || '#3b82f6';
}

/**
 * Get header text based on notification type
 */
function getHeaderByType(type) {
    const headers = {
        success: 'Success',
        error: 'Error',
        warning: 'Warning',
        info: 'Info'
    };
    return headers[type] || 'Notification';
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Validate input
 */
function validateInput(input, type = 'text') {
    const value = input.value.trim();
    
    switch(type) {
        case 'name':
            if (!value) {
                input.classList.add('is-invalid');
                return false;
            }
            if (value.length < 2) {
                input.classList.add('is-invalid');
                return false;
            }
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            return true;
            
        case 'email':
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                input.classList.add('is-invalid');
                return false;
            }
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            return true;
            
        case 'date':
            if (!value) {
                input.classList.add('is-invalid');
                return false;
            }
            input.classList.remove('is-invalid');
            input.classList.add('is-valid');
            return true;
            
        default:
            return !!value;
    }
}

/**
 * Format date to readable format
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
}

/**
 * Format time to readable format
 */
function formatTime(timeString) {
    const [hours, minutes, seconds] = timeString.split(':');
    return `${hours}:${minutes}`;
}

/**
 * Debounce function for search
 */
function debounce(func, wait) {
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

/**
 * Generate unique ID
 */
function generateId() {
    return 'id_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Check if device is mobile
 */
function isMobileDevice() {
    return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
}

/**
 * Request full screen for camera
 */
async function requestFullscreen(element) {
    if (element.requestFullscreen) {
        await element.requestFullscreen();
    } else if (element.webkitRequestFullscreen) {
        await element.webkitRequestFullscreen();
    }
}

/**
 * Clean up on page unload
 */
window.addEventListener('beforeunload', () => {
    stopCamera();
});

/**
 * Handle page visibility to pause/resume camera
 */
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        // Page is hidden, stop camera to save battery
        // stopCamera();
    } else {
        // Page is visible, restart camera if needed
        // startCamera();
    }
});

// Initialize tooltips and popovers if Bootstrap is available
document.addEventListener('DOMContentLoaded', () => {
    // Initialize Bootstrap tooltips
    if (window.bootstrap) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(tooltipTriggerEl => new window.bootstrap.Tooltip(tooltipTriggerEl));

        // Initialize Bootstrap popovers
        const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.map(popoverTriggerEl => new window.bootstrap.Popover(popoverTriggerEl));
    }
});

/**
 * Log function for debugging
 */
function log(message, data = null) {
    if (data) {
        console.log(`[FaceAttend] ${message}`, data);
    } else {
        console.log(`[FaceAttend] ${message}`);
    }
}

