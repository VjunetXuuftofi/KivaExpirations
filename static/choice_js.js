/**
 * Created by thomaswoodside on 9/9/16.
 */
console.log("test");
document.getElementById("submit").onclick =
    function() {
    var stuff = document.getElementById('link').value.split("/");
    window.location = stuff[stuff.length-1];
};