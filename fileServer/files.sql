drop table if exists files;
create table files (
  filename text primary key,
  body text not null,
  version integer not null,
  lock integer not null,
  level integer not null
);