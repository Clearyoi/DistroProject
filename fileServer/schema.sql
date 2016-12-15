drop table if exists files;
create table files (
  filename text primary key,
  body text not null
);