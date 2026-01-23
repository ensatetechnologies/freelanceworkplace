/* Freelance Marketplace - Main JavaScript */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize components
    initNotifications();
    initMessagePolling();
    initFormValidation();
    initConfirmDialogs();
});

/**
 * Notifications
 */
function initNotifications() {
    const notificationBadge = document.getElementById('notification-badge');
    const notificationList = document.getElementById('notification-list');
    
    if (!notificationBadge) return;
    
    // Fetch notification count
    function updateNotificationCount() {
        fetch('/notifications/unread-count/')
            .then(response => response.json())
            .then(data => {
                if (data.unread_count > 0) {
                    notificationBadge.textContent = data.unread_count;
                    notificationBadge.classList.remove('d-none');
                } else {
                    notificationBadge.classList.add('d-none');
                }
            })
            .catch(err => console.log('Error fetching notifications:', err));
    }
    
    // Update every 30 seconds
    updateNotificationCount();
    setInterval(updateNotificationCount, 30000);
    
    // Load notifications on dropdown open
    const notificationDropdown = document.querySelector('.notification-dropdown');
    if (notificationDropdown) {
        notificationDropdown.addEventListener('show.bs.dropdown', function() {
            fetch('/notifications/dropdown/')
                .then(response => response.json())
                .then(data => {
                    if (data.notifications && data.notifications.length > 0) {
                        notificationList.innerHTML = data.notifications.map(n => `
                            <a href="${n.action_url || '#'}" class="dropdown-item py-2 ${n.is_read ? '' : 'bg-light'}">
                                <div class="d-flex justify-content-between">
                                    <strong class="small">${n.title}</strong>
                                    <small class="text-muted">${formatTimeAgo(n.created_at)}</small>
                                </div>
                                <small class="text-muted">${n.message}</small>
                            </a>
                        `).join('');
                    } else {
                        notificationList.innerHTML = '<p class="text-muted text-center py-3 mb-0">No new notifications</p>';
                    }
                })
                .catch(err => console.log('Error loading notifications:', err));
        });
    }
}

/**
 * Message Polling for Chat
 */
function initMessagePolling() {
    const chatContainer = document.querySelector('.chat-container');
    if (!chatContainer) return;
    
    const conversationId = chatContainer.dataset.conversationId;
    const messagesContainer = document.querySelector('.chat-messages');
    let lastMessageId = null;
    
    function pollMessages() {
        let url = `/messages/${conversationId}/fetch/`;
        if (lastMessageId) {
            url += `?last_id=${lastMessageId}`;
        }
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (data.messages && data.messages.length > 0) {
                    data.messages.forEach(msg => {
                        appendMessage(msg);
                        lastMessageId = msg.id;
                    });
                    scrollToBottom();
                }
            })
            .catch(err => console.log('Error polling messages:', err));
    }
    
    function appendMessage(msg) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${msg.is_mine ? 'message-sent' : 'message-received'}`;
        messageDiv.innerHTML = `
            <div class="message-bubble">
                <p class="mb-1">${msg.content}</p>
                <small class="text-${msg.is_mine ? 'light' : 'muted'}">${formatTime(msg.created_at)}</small>
            </div>
        `;
        messagesContainer.appendChild(messageDiv);
    }
    
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Poll every 3 seconds
    setInterval(pollMessages, 3000);
    scrollToBottom();
}

/**
 * Form Validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Confirm Dialogs
 */
function initConfirmDialogs() {
    document.querySelectorAll('[data-confirm]').forEach(element => {
        element.addEventListener('click', function(event) {
            const message = this.dataset.confirm || 'Are you sure?';
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });
}

/**
 * Helper Functions
 */
function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return Math.floor(seconds / 60) + 'm ago';
    if (seconds < 86400) return Math.floor(seconds / 3600) + 'h ago';
    if (seconds < 604800) return Math.floor(seconds / 86400) + 'd ago';
    
    return date.toLocaleDateString();
}

function formatTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * AJAX Form Submission
 */
function submitForm(form, callback) {
    const formData = new FormData(form);
    const csrfToken = getCookie('csrftoken');
    
    fetch(form.action, {
        method: form.method || 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (callback) callback(data);
    })
    .catch(err => {
        console.error('Form submission error:', err);
    });
}

/**
 * Save Project Toggle
 */
function toggleSaveProject(projectSlug, button) {
    const csrfToken = getCookie('csrftoken');
    
    fetch(`/projects/${projectSlug}/save/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        const icon = button.querySelector('i');
        if (data.saved) {
            icon.classList.remove('bi-bookmark');
            icon.classList.add('bi-bookmark-fill');
            button.classList.add('text-primary');
        } else {
            icon.classList.remove('bi-bookmark-fill');
            icon.classList.add('bi-bookmark');
            button.classList.remove('text-primary');
        }
    })
    .catch(err => console.error('Error toggling save:', err));
}
