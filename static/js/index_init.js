document.getElementById('myForm').addEventListener('submit', function (event) {
    
    // Show loading screen
    document.getElementById('loadingScreen').style.display = 'flex';

    // Simulate submission delay (You can replace this with actual form submission logic)
    setTimeout(function () {
        // Hide loading screen after a delay (simulating submission success)
        document.getElementById('loadingScreen').style.display = 'none';
        
    }, 10000); // Replace 3000 with your desired delay in milliseconds
});
