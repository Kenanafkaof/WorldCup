function getStats(team) {
    const url = `http://127.0.0.1:5000/team?t=${team}`
    location.href = url
}

function hideModal() {
    $("#standings-modal").removeClass("show")
    $("#standings-modal").addClass("hide")
}

function backHome() {
    const url = "http://127.0.0.1:5000/bracket"
    location.href = url
}