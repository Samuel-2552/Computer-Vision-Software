const selectDirectory = (e) => {
    var id = e.target.dataset.locationid;
    $.get('/select_directory', function (response) {
        document.getElementById(id).value = response;
    });
}

const btn = document.querySelectorAll("button[type='button']")
btn.forEach(btn => {
    btn.addEventListener('click', selectDirectory)
})


function validateForm() {
    var projectLocation = document.getElementById("projectLocation").value;
    if (projectLocation.trim() === "") {
        // alert("Project Location cannot be empty.");
        displayAlertBox("Project Location cannot be empty.");
        return false; // Prevent form submission
    }
    return true; // Allow form submission
}

function displayAlertBox(message) {
    var alertBox = document.getElementById("customAlertBox");
    var alertMessage = document.getElementById("alertMessage");
    alertMessage.innerHTML = message;
    alertBox.style.display = "block";
    disableFormInteraction(true);
}

function closeAlertBox() {
    var alertBox = document.getElementById("customAlertBox");
    alertBox.style.display = "none";
    disableFormInteraction(false);
}

function disableFormInteraction(disable) {
    var form = document.getElementById("myForm");
    var elements = form.elements;
    for (var i = 0; i < elements.length; i++) {
        elements[i].disabled = disable;
    }
}
