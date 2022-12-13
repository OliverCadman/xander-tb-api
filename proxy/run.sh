#!/bin/sh

set -e

envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
nginx -g 'daemon off;'

RED='\033[0;31m'
echo -e "${RED}Remember to update DJANGO_ALLOWED_HOSTS with the new AWS URL!!${NC}"