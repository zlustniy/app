#!/usr/bin/env bash

set -e
cmd="$@"
/wait
echo "Starting ... $cmd"

case "$1" in
  gunicorn) /commands/web.sh ;;
  test ) /commands/test.sh ;;
  *) exec $@ ;;
esac
