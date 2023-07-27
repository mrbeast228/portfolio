DROP DATABASE IF EXISTS bebra228;

CREATE DATABASE bebra228;

USE bebra228;

CREATE TABLE vitsan (
	id int not null auto_increment,
	name varchar(255) not null,
	unique(name),
	score int not null default 0,
	primary key(id)
);
