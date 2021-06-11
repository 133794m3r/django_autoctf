#!/usr/bin/bash
#
# Macarthur Inbody <admin-contact@transcendental.us>
# Licensed under LGPLv3 Or Later (2020)
#

sudo su - postgres -c 'createuser django -d -P && psql -f postgres_config.sql'
