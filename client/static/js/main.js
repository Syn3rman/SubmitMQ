$( document ).ready(function() {
    $("#file-upload").css("opacity", "0");  

    $("#file-browser").on("click", function(){
        $("#file-upload").click();
    });
});