#
# Macarthur Inbody <admin-contact@transcendental.us>
# Licensed under LGPLv3 Or Later (2020)
#

#!/usr/bin/bash
sudo su postgres;
createuser django -d -P
psql -f postgres_config.sql