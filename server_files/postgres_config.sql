-- This file will setup the database file and also grant the priviledges to django and do other psql stuff.
create database django;
create database ctf_club;
grant all privileges on database django to django;
grant all privileges on database ctf_club to django;
alter role django set client_encoding to 'utf8';
alter role django set default_transaction_isolation to "read committed";
alter role django set timezone to 'UTC';
