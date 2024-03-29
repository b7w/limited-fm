function Notify(message) {
    jQuery( '.messagelist' ).append( '<li class="info">' + message + '</li>' );
}
function NotifyError(message) {
    jQuery( '.messagelist' ).append( '<li class="error">' + message + '</li>' );
}

function Trash(obj) {

    var data = jQuery.parseJSON( jQuery( obj ).parent().parent().parent().children( '.info' ).text() );
    var flag = confirm( "Do you realy want to delete " + jQuery.trim( data.name ) + "?" );

    if (flag == true) {
        var link = "/lib" + data.home + "/action/trash/?p=" + data.path;
        window.location = link;
    }
}

function Delete(obj) {

    var data = jQuery.parseJSON( jQuery( obj ).parent().parent().parent().children( '.info' ).text() );
    var flag = confirm( "Do you realy want to delete " + jQuery.trim( data.name ) + "?" );

    if (flag == true) {
        var link = "/lib" + data.home + "/action/delete/?p=" + data.path;
        window.location = link;
    }
}

function Rename(obj) {
    var data = jQuery.parseJSON( jQuery( obj ).parent().parent().parent().children( '.info' ).text() );
    var name = prompt( 'Enter new name', jQuery.trim( data.name ) );

    if (name != null && name != "") {
        var link = "/lib" + data.home + "/action/rename/?p=" + data.path + "&amp;n=" + encodeURIComponent( name );
        window.location = link;
    }
}

function Move(obj) {

    var data = jQuery.parseJSON( jQuery( obj ).parent().parent().parent().children( '.info' ).text() );
    var path2 = prompt( 'Enter new path', '' );

    if (path2 != null && path2 != "") {
        var link = "/lib" + data.home + "/action/move/?p=" + data.path + "&amp;p2=" + encodeURIComponent( path2 );
        window.location = link;
    }
}

function Link(obj) {
    var data = jQuery.parseJSON( jQuery( obj ).parent().parent().parent().children( '.info' ).text() );

    link = "/lib" + data.home + "/action/link/?p=" + data.path;
    window.location = link;
}

function Zip(obj) {
    var data = jQuery.parseJSON( jQuery( obj ).parent().parent().parent().children( '.info' ).text() );

    link = "/lib" + data.home + "/action/zip/?p=" + data.path;
    window.location = link;
}

function Size(obj) {
    var data = jQuery.parseJSON( jQuery( obj ).parent().children( '.info' ).text() );

    var link = "/lib" + data.home + "/action/size/?p=" + data.path;
    jQuery.get( link, function (size) {
        jQuery( obj ).text( size );
    } );
}

function handleFileSelect(event, allowed, except, message) {
    var files = event.target.files;
    var allowed = allowed.split( '|' );
    var except = except.split( '|' );
    var flag = false;
    console.log( allowed )
    console.log( except )
    for (var i = 0, f; f = files[i]; i++) {
        for (var j = 0, a; a = allowed[j]; j++) {
            if (!f.name.match( a )) {
                flag = true
            }
        }
        for (var j = 0, e; e = except[j]; j++) {
            if (f.name.match( e )) {
                flag = true
            }
        }
        if (flag == true) {
            NotifyError( message.replace('{0}', f.name) )
        }
    }
    if (flag == true) {
        var fr = document.getElementById( 'files' );
        fr.form.reset();
        fr.focus();
    }
}

function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace( /[?&]+([^=&]+)=([^&]*)/gi, function (m, key, value) {
        vars[key] = value;
    } );
    return vars;
}
