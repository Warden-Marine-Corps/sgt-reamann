DROP DATABASE IF EXISTS Reamann;

CREATE DATABASE Reamann;

USE Reamann;

CREATE TABLE WebsiteAuth(
	website_auth_id INT AUTO_INCREMENT,
	access_token VARCHAR(64),
	refresh_token VARCHAR(64),
	remaining_time_token TIMESTAMP,
	`hash` VARCHAR(64),
	user_id BIGINT(11) NOT NULL,
	`remaining_time_hash` TIMESTAMP,
	CONSTRAINT PK_WebsiteAuth PRIMARY KEY(website_auth_id)
);

CREATE TABLE BotCommands(
	command_id INT AUTO_INCREMENT,
	command_name VARCHAR(64) NOT NULL,
	command_description VARCHAR(512) NOT NULL,
	CONSTRAINT PK_BotCommands PRIMARY KEY(command_id)
);

CREATE TABLE Param(
	param_number INT,
	command_id INT,
	param_name VARCHAR(2048),
	param_desc VARCHAR(2048),
	param_type VARCHAR(64),
	is_optional BOOL,
	`default` VARCHAR(2048),
	CONSTRAINT PK_Param PRIMARY KEY(param_number, command_id),
	CONSTRAINT FK_Param_command_id FOREIGN KEY (command_id)
        REFERENCES BotCommands(command_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE

);

CREATE TABLE `Event`(
	event_id INT AUTO_INCREMENT,
	event_name VARCHAR(64) NOT NULL,
	event_date TIMESTAMP NOT NULL,
	event_description VARCHAR(2048),
	min_user_count INT,
	max_user_count INT,
	event_picture VARCHAR(2048),
	guild_id BIGINT(11) NOT NULL,
	channel_id BIGINT(11) NOT NULL,
	role_id BIGINT(11),
	message_id BIGINT(11),
	creator_id BIGINT(11),
	CONSTRAINT PK_Event PRIMARY KEY(event_id)
);

CREATE TABLE Participant(
	participant_id INT AUTO_INCREMENT,
	event_id INT,
	user_id BIGINT(11),
	participant_type INT,
	CONSTRAINT PK_Participant PRIMARY KEY(participant_id),
	CONSTRAINT FK_Participant_event_id FOREIGN KEY (event_id)
        REFERENCES `Event`(event_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE TicketConfig(
	ticket_config_id INT AUTO_INCREMENT,
	guild_id BIGINT(11),
	support_role_id BIGINT(11),
	ticket_category_id BIGINT(11),
	closed_category_id BIGINT(11),
	log_channel_id BIGINT(11),
	CONSTRAINT PK_TicketConfig PRIMARY KEY(ticket_config_id)
);

CREATE TABLE SelfRoleBlock(
	self_role_block_id INT AUTO_INCREMENT,
	message VARCHAR(2048),
	guild_id BIGINT(11),
	CONSTRAINT PK_SelfRoleBlock PRIMARY KEY(self_role_block_id)

);

CREATE TABLE SelfRoleRole(
	self_role_role_id INT AUTO_INCREMENT,
	self_role_block_id INT,
	role_id BIGINT(11),
	`name` VARCHAR(64),
	emoji VARCHAR(64) CHARACTER SET utf8mb4 NOT NULL,
	CONSTRAINT PK_SelfRoleRole PRIMARY KEY(self_role_role_id),
	CONSTRAINT FK_self_role_block_id FOREIGN KEY (self_role_block_id)
        REFERENCES SelfRoleBlock(self_role_block_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE MultiEvent(
	multi_event_id INT,
	event_id INT,
	guild_id BIGINT(11),
	message_id BIGINT(11),
	CONSTRAINT PK_MultiEvent PRIMARY KEY(multi_event_id),
	CONSTRAINT FK_multi_event_id FOREIGN KEY (event_id)
        REFERENCES `Event`(event_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE

);

CREATE TABLE ParticipantType(
	participant_type_id INT AUTO_INCREMENT,
	type_name VARCHAR(64) CHARACTER SET utf8mb4 NOT NULL,
	event_id INT,
	CONSTRAINT PK_ParticipantType PRIMARY KEY(participant_type_id),
	CONSTRAINT FK_ParticipantType_event_id FOREIGN KEY (event_id)
        REFERENCES `Event`(event_id)
        ON DELETE CASCADE
        ON UPDATE CASCADEReamann
	
);