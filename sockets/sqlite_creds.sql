create table [credentials] (
	[user_id] integer primary key,
	[username] text not null unique,
	[password] text not null,
	[is_admin] text not null,
	[discount] text not null
);