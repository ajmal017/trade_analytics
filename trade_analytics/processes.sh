#!/usr/bin/env bash
export Queues=ML,charts,celery
celery -A proj worker -Q celery --loglevel=INFO --concurrency=5 -n worker1@%h --logfile=celeryinfo/%p.log --pidfile=celeryinfo/%n.pid
celery -A proj worker -Q ML 	--loglevel=INFO --concurrency=1 -n worker2@%h --logfile=celeryinfo/%p.log --pidfile=celeryinfo/%n.pid
celery -A proj worker -Q charts --loglevel=INFO --concurrency=5 -n worker3@%h --logfile=celeryinfo/%p.log --pidfile=celeryinfo/%n.pid




# pkill -9 -f 'celery worker'