create table users
(
	id serial
		constraint users_pk
			primary key,
	first_name varchar(64) not null,
	last_name varchar(64) not null,
	is_tutor bool not null,
	created timestamp
);
