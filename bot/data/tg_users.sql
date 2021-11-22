create table tg_users
(
	id serial
		constraint tg_users_pk
			primary key,
	tg_id bigint not null,
	username varchar(256) not null
);

