# -*- coding: utf-8 -*-

from optparse import make_option

from django.core.management.base import NoArgsCommand, CommandError
from django.core.management.color import no_style
from django.db import connections, transaction, DEFAULT_DB_ALIAS

from limited.core.models import Permission
from limited.core.management.utils import load_permissions

class Command( NoArgsCommand ):
    help = "Flush Permissons table and generat new data for any count of columns in Permission"

    option_list = NoArgsCommand.option_list + (
        make_option( '--noinput', action='store_false', dest='interactive', default=True,
                     help='Tells Django to NOT prompt the user for input of any kind.' ),
        make_option( '--database', action='store', dest='database',
                     default=DEFAULT_DB_ALIAS, help='Nominates a database to print the '
                                                    'SQL for.  Defaults to the "default" database.' ),
        )

    def handle_noargs(self, **options):
        db = options.get( 'database', DEFAULT_DB_ALIAS )
        connection = connections[db]
        interactive = options.get( 'interactive' )

        self.style = no_style( )

        sql_list = connection.ops.sql_flush( self.style, [Permission._meta.db_table],
                                             connection.introspection.sequence_list( ) )

        if interactive:
            confirm = raw_input( """You have requested a flush of the Permission table.
This will IRREVERSIBLY DESTROY all data, and load new.
Are you sure you want to do this?

    Type 'yes' to continue, or 'no' to cancel: """ )
            print
        else:
            confirm = 'yes'

        if confirm == 'yes':
            # execute flush 
            try:
                cursor = connection.cursor( )
                for sql in sql_list:
                    cursor.execute( sql )
                if interactive:
                    print "Permissions flushed."
                transaction.commit_on_success( using=db )( load_permissions )( using=db )
                if interactive:
                    print "%s permissions loaded." % Permission.objects.count( )
            except Exception, e:
                transaction.rollback_unless_managed( using=db )
                if interactive:
                    print "Rollback."
                raise CommandError( """Permissions couldn't be load. \nThe full error: %s""" % e )

            transaction.commit_unless_managed( using=db )

        else:
            if interactive:
                print "Cancelled."
        
        
        
