#!/bin/bash

USER=limited
GROUP=limited
WWWUSER=www-data

# Path to dir with manage.py
ROOT=/some/../path/limitedfm

# dir for pidfile
RUN=/var/run/limitedfm

ARGS="workdir=$ROOT socket=$RUN/fcgi.sock pidfile=$RUN/fcgi.pid maxspare=4 maxchildren=8 --settings=settings"

start() {
        echo -n "Starting Django FastCGI: "
        if [ ! -d $RUN ]; then
                mkdir $RUN
                touch $RUN/fcgi.sock
                touch $RUN/fcgi.pid
                chown $USER:$WWWUSER -R $RUN
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
