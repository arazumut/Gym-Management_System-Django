// DOM yüklendikten sonra çalışacak kodlar
document.addEventListener('DOMContentLoaded', function() {
    // Bootstrap tooltips'i etkinleştir
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Bootstrap popovers'ı etkinleştir
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Otomatik kapanan uyarılar
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Mobil menü toggle
    var sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            document.querySelector('.sidebar').classList.toggle('show');
        });
    }
    
    // Form doğrulama
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Tarih seçicileri için varsayılan format
    var dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        if (!input.value) {
            var today = new Date();
            var dd = String(today.getDate()).padStart(2, '0');
            var mm = String(today.getMonth() + 1).padStart(2, '0');
            var yyyy = today.getFullYear();
            
            if (input.hasAttribute('data-default-today')) {
                input.value = yyyy + '-' + mm + '-' + dd;
            }
        }
    });
    
    // Tablo sıralama
    var sortableTables = document.querySelectorAll('.table-sortable');
    sortableTables.forEach(function(table) {
        var headers = table.querySelectorAll('th[data-sort]');
        headers.forEach(function(header) {
            header.addEventListener('click', function() {
                var sortKey = this.getAttribute('data-sort');
                var sortDirection = this.getAttribute('data-sort-direction') || 'asc';
                var newDirection = sortDirection === 'asc' ? 'desc' : 'asc';
                
                // Tüm başlıkların yönünü sıfırla
                headers.forEach(function(h) {
                    h.setAttribute('data-sort-direction', '');
                    h.querySelector('.sort-icon').innerHTML = '<i class="fas fa-sort"></i>';
                });
                
                // Bu başlığın yönünü ayarla
                this.setAttribute('data-sort-direction', newDirection);
                var icon = newDirection === 'asc' ? '<i class="fas fa-sort-up"></i>' : '<i class="fas fa-sort-down"></i>';
                this.querySelector('.sort-icon').innerHTML = icon;
                
                // Tabloyu sırala
                sortTable(table, sortKey, newDirection);
            });
        });
    });
    
    // Arama filtreleme
    var searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(function(input) {
        input.addEventListener('keyup', function() {
            var tableId = this.getAttribute('data-table');
            var table = document.getElementById(tableId);
            var searchText = this.value.toLowerCase();
            
            var rows = table.querySelectorAll('tbody tr');
            rows.forEach(function(row) {
                var text = row.textContent.toLowerCase();
                if (text.indexOf(searchText) > -1) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
});

// Tablo sıralama fonksiyonu
function sortTable(table, sortKey, direction) {
    var tbody = table.querySelector('tbody');
    var rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort(function(a, b) {
        var aValue = a.querySelector('[data-sort-value="' + sortKey + '"]').getAttribute('data-sort-value');
        var bValue = b.querySelector('[data-sort-value="' + sortKey + '"]').getAttribute('data-sort-value');
        
        // Sayısal değerler için
        if (!isNaN(aValue) && !isNaN(bValue)) {
            return direction === 'asc' ? aValue - bValue : bValue - aValue;
        }
        
        // Metin değerleri için
        return direction === 'asc' ? 
            aValue.localeCompare(bValue) : 
            bValue.localeCompare(aValue);
    });
    
    // Sıralanmış satırları tabloya ekle
    rows.forEach(function(row) {
        tbody.appendChild(row);
    });
}

// AJAX form gönderimi
function submitFormAjax(formId, successCallback, errorCallback) {
    var form = document.getElementById(formId);
    var formData = new FormData(form);
    
    fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (successCallback) successCallback(data);
        } else {
            if (errorCallback) errorCallback(data);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        if (errorCallback) errorCallback({success: false, message: 'Bir hata oluştu.'});
    });
    
    return false;
}

// Bildirim gösterme
function showNotification(message, type = 'info', duration = 5000) {
    var notification = document.createElement('div');
    notification.className = 'toast show';
    notification.setAttribute('role', 'alert');
    notification.setAttribute('aria-live', 'assertive');
    notification.setAttribute('aria-atomic', 'true');
    
    notification.innerHTML = `
        <div class="toast-header bg-${type} text-white">
            <strong class="me-auto">Bildirim</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    var container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(container);
    }
    
    container.appendChild(notification);
    
    setTimeout(function() {
        notification.remove();
    }, duration);
}

// Onay kutusu
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// Para formatı
function formatCurrency(amount, currency = '₺') {
    return amount.toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,') + ' ' + currency;
}

// Tarih formatı
function formatDate(dateString) {
    var date = new Date(dateString);
    var day = String(date.getDate()).padStart(2, '0');
    var month = String(date.getMonth() + 1).padStart(2, '0');
    var year = date.getFullYear();
    
    return day + '.' + month + '.' + year;
}

// Sayfa yükleme göstergesi
function showLoading() {
    var loading = document.createElement('div');
    loading.className = 'loading-overlay';
    loading.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="visually-hidden">Yükleniyor...</span></div>';
    document.body.appendChild(loading);
}

function hideLoading() {
    var loading = document.querySelector('.loading-overlay');
    if (loading) {
        loading.remove();
    }
} 