drop table if exists users;
create table users (
  username text primary key,
  password text not null,
  level text not null
);