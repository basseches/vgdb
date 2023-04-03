$(document).ready(function() {
    $("#searchbtn").submit(function(event) {
        event.preventDefault();
        submitSearch()
    });
})

function submitSearch() {
    let search = $.trim($("#search").val())
    if (search != "") {
        window.location.replace("/query/all/" + search);
    }
}