const selectDirectory = (e) => {
    var id = e.target.dataset.locationid;
    $.get('/select_directory', function (response) {
        document.getElementById(id).value = response;
    });
}

const btn = document.querySelectorAll("button[type='button']")
btn.forEach( btn => {
    btn.addEventListener('click', selectDirectory)
})