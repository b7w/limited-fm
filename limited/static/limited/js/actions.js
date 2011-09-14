function Notify( message ) {
    jQuery('.messagelist').append('<li class="info">'+message+'</li>');
}
function NotifyError( message ) {
    jQuery('.messagelist').append('<li class="error">'+message+'</li>');
}
function NotifyWarning( message ) {
    jQuery('.messagelist').append('<li class="warning">'+message+'</li>');
}

function Trash( obj ) {

    var data = jQuery.parseJSON( jQuery(obj).parent().parent().parent().children('.info').text() );
    var flag = confirm("Do you realy want to delete " + jQuery.trim(data.name) + "?");

    if ( flag == true )
    {
        var link = "/lib"+data.home+"/action/trash/?p="+data.path;
        window.location = link;
    }
    else
    {
        NotifyWarning('Deleting canceled by user');
    }
}

function Delete( obj ) {

    var data = jQuery.parseJSON( jQuery(obj).parent().parent().parent().children('.info').text() );
    var flag = confirm("Do you realy want to delete " + jQuery.trim(data.name) + "?");

    if ( flag == true )
    {
        var link = "/lib"+data.home+"/action/delete/?p="+data.path;
        window.location = link;
    }
    else
    {
        NotifyWarning('Deleting canceled by user');
    }
}

function Rename( obj ) {
    var data = jQuery.parseJSON( jQuery(obj).parent().parent().parent().children('.info').text() );
    var name = prompt( 'Enter new name', jQuery.trim(data.name) );

    if (name!=null && name!="")
    {
        var link = "/lib"+data.home+"/action/rename/?p="+data.path+"&amp;n=" + encodeURIComponent(name);
        window.location = link;
    }
    else {
        NotifyWarning('Rename canceled by user');
    }
}

function Move( obj ) {

    var data = jQuery.parseJSON( jQuery(obj).parent().parent().parent().children('.info').text() );
    var path2 = prompt( 'Enter new path', '' );
    
    if (path2!=null && path2!="")
    {
        var link = "/lib"+data.home+"/action/move/?p="+data.path+"&amp;p2=" + encodeURIComponent(path2);
        window.location = link;
    }
    else {
        NotifyWarning('Moving canceled by user');
    }
}

function Link( obj ) {
    var data = jQuery.parseJSON( jQuery(obj).parent().parent().parent().children('.info').text() );

    link = "/lib"+data.home+"/action/link/?p="+data.path;
    window.location = link;
}

function Zip( obj ) {
    var data = jQuery.parseJSON( jQuery(obj).parent().parent().parent().children('.info').text() );

    link = "/lib"+data.home+"/action/zip/?p="+data.path;
    window.location = link;
}

function Size( obj ) {
    var data = jQuery.parseJSON( jQuery(obj).parent().children('.info').text() );

    var link = "/lib"+data.home+"/action/size/?p="+data.path;
    jQuery.get( link, function( size ){
       jQuery(obj).text( size );
    });
}