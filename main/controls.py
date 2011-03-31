from django.contrib.auth.models import User
from django.http import Http404

from main.models import MHome

# Get authenticated user
# or anonymous user if he had any FileLibs
# or None
def get_user( request ):
    if request.user.is_authenticated( ):
        return request.user

    elif request.user.is_anonymous( ):
        Anonymous = User.objects.get( username__exact='Anonymous' )
        AnonymousLibs = MHome.objects.filter( user=Anonymous.id ).count( )
        if AnonymousLibs == 0:
            return None
        return Anonymous

def get_params( request ):
    if 'h' in request.GET:
        home = int( request.GET['h'] )
    else:
        raise Http404('Bag http request')

    if 'p' in request.GET:
        path = request.GET['p']
    else:
        path = ''
        
    return ( home, path )