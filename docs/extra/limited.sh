#!/bin/bash

USER=www-data
GROUP=www-data

# Path to dir with manage.py
ROOT=/some/../path/FileManager

# dir for pidfile
RUN=/var/run/limited

ARGS="workdir=$ROOT socket=$RUN/fcgi.sock pidfile=$RUN/fcgi.pid maxspare=4 maxchildren=8 --settings=settings"

start() {
        echo -n "Starting Django FastCGI: "
        if [ ! -d $RUN ]; then
                mkdir $RUN
                chown $USER:$GROUP -R $RUN
        fi
        su $USER -c "python $ROOT/manage.py runfcgi $ARGS"

        RETVAL=$?
        echo "FastCGI Django."
}

stop() {
        echo -n "Stopping Django FastCGI: "
        kill `cat $RUN/fcgi.pid`
        RETVAL=$?
        echo "FastCGI Django."
}

case "$1" in
        start)
                start
        ;;
        stop)
                stop
        ;;
        restart)
                stop
                start
        ;;
        *)
                echo "Usage: django-fastcgi {start|stop|restart}"
                exit 1
        ;;

esac

exit $RETVAL
