drop table if exists files;
create table files (
  filename text primary key,
  body text not null,
  version integer not null,
  lock text,
  lockLevel integer,
  level integer not null
);