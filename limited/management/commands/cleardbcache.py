# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from limited.management.utils import clear_db_cache

class Command( BaseCommand ):
    args = u"[time]"
    help = u"Clear database filelib cache in all filelibs. Default Time -a week.\nSample: cleardbcache '7*24*60*60'"

    def handle(self, *args, **options):
        self.style = no_style( )
        if len( args ) == 0:
            clear_db_cache( )
        else:
            time = eval( args[0] )
            clear_db_cache( time )
#            try:
#                time = eval( args[0] )
#                clear_db_cache( time )
#            except Exception as e:
#                raise CommandError( e )