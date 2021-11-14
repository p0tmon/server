create table device(
  id varchar primary key,
  lon float not null,
  lat float not null
);

create table log(
  id varchar not null,
  time text not null,
  -- event int not null,
  -- confidence int not null, /* percentage confidence */
  foreign key(id) references device(id)
);