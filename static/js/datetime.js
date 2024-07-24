function updateDateTime() {
    var now = new Date();
    
    var optionsFull = {
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric', 
        hour: 'numeric', 
        minute: 'numeric', 
        second: 'numeric'
    };

    var optionsShort = {
        year: 'numeric', 
        month: 'short', 
        day: 'numeric', 
        hour: 'numeric', 
        minute: 'numeric'
    };

    var formattedDateTime;

    if (window.innerWidth > 575) {
        formattedDateTime = now.toLocaleDateString('en-US', optionsFull);
    } else {
        formattedDateTime = now.toLocaleDateString('en-US', optionsShort);
    }

    document.getElementById('currentDateTime').textContent = formattedDateTime;
}

// Panggil fungsi pertama kali untuk mengisi elemen
updateDateTime();

// Update setiap detik
setInterval(updateDateTime, 1000);

// Update format ketika ukuran layar berubah
window.onresize = updateDateTime;