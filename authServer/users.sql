drop table if exists users;
create table users (
  username text primary key,
  password text not null,
  level integer not null
);
insert into users values ("admin", "password", 1);