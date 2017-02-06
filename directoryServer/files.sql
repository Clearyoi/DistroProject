drop table if exists files;
create table files (
  filename text primary key,
  version integer not null,
  lock text,
  lockLevel integer,
  level integer not null
);