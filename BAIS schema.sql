CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  email varchar(50) UNIQUE NOT NULL,
  password text NOT NULL,
  created_at timestamp NOT NULL
);

CREATE TABLE IF NOT EXISTS history (
  id SERIAL PRIMARY KEY,
  user_id int NULL,
  category_id int NOT NULL,
  name varchar(100) NOT NULL,
  url text NOT NULL,
  created_at timestamp NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users(id)
);