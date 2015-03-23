DROP DATABASE IF EXISTS session; 
CREATE DATABASE session;
\c session;
CREATE EXTENSION pgcrypto;


CREATE TABLE IF NOT EXISTS users (
  id serial,
  username varchar(12) NOT NULL,
  password varchar(126) NOT NULL,
  zipcode int NOT NULL,
  PRIMARY KEY (id)
)  ;

--
-- Dumping data for table `users`
--

INSERT INTO users (username, password, zipcode) VALUES
('raz', crypt('p00d13',gen_salt('bf')), 88005),
('ann', crypt('changeme',gen_salt('bf')), 22401),
('lazy', crypt('qwerty', gen_salt('bf')), 22401);

CREATE TABLE IF NOT EXISTS messages (
  id serial, 
  username varchar(12) NOT NULL, 
  message varchar(150) NOT NULL, 
  PRIMARY KEY (id)
) ;

INSERT INTO messages (username, message) VALUES 
('raz', 'I love computer science');   