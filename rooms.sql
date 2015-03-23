DROP DATABASE IF EXISTS room_session; 
CREATE DATABASE room_session;
\c room_session;
CREATE EXTENSION pgcrypto;

DROP TABLE IF EXISTS room_info; 
CREATE TABLE IF NOT EXISTS room_info (

    id serial, 
    room int NOT NULL, 
    PRIMARY KEY (id)
    
) ; 

DROP TABLE IF EXISTS users_room;
CREATE TABLE IF NOT EXISTS users_room (
    user_id int NOT NULL, 
    room_id int NOT NULL,
    PRIMARY KEY (user_id, room_id)  
); 

DROP TABLE IF EXISTS users; 
CREATE TABLE IF NOT EXISTS users (
  id serial,
  username varchar(12) NOT NULL,
  password varchar(126) NOT NULL,
  PRIMARY KEY (id)
)  ;

--
-- Dumping data for table `users`
--

INSERT INTO users (username, password) VALUES
('raz', crypt('p00d13',gen_salt('bf'))),
('ann', crypt('changeme',gen_salt('bf'))),
('lazy', crypt('qwerty', gen_salt('bf')));

DROP TABLE IF EXISTS messages; 
CREATE TABLE IF NOT EXISTS messages (
  id serial, 
  username varchar(12) NOT NULL, 
  message varchar(150) NOT NULL, 
  PRIMARY KEY (id)
) ;

INSERT INTO messages (username, message) VALUES 
('raz', 'I love computer science'); 