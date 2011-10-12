# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from limited.management.utils import clear_folders

class Command( BaseCommand ):
    args = u"path [time]"
    help = u"Clear folder in all filelibs. If no folder - nothing will happend. Default Time -a week.\nSample: clearfolder .TrashBin '7*24*60*60'"

    def handle(self, *args, **options):
        self.style = no_style( )
        if len( args ) == 0:
            raise CommandError( u"Need path to the folder" )
        elif len( args ) == 1:
            path = args[0]
            clear_folders( path )
        else:
            try:
                path = args[0]
                time = eval( args[1] )
                clear_folders( path, time )
            except Exception as e:
                raise CommandError( e )