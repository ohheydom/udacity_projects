-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;
\c tournament

CREATE TABLE players
  (
    id serial primary key,
    player_name varchar(50)
  );

CREATE TABLE matches
  (
    id serial primary key,
    winner integer references players (id),
    loser integer references players (id)
  );

CREATE VIEW match_wins AS SELECT players.id AS player_id,
                                 count(matches.winner) AS num_wins
                          FROM players LEFT JOIN matches ON players.id = matches.winner
                          GROUP BY players.id;

CREATE VIEW match_losses AS SELECT players.id AS player_id,
                                   count(matches.loser) AS num_losses
                            FROM players LEFT JOIN matches ON players.id = matches.loser
                            GROUP BY players.id;

CREATE VIEW match_totals AS SELECT match_wins.player_id,
                                   (match_losses.num_losses + match_wins.num_wins) AS num_matches,
                                   match_wins.num_wins AS num_wins
                            FROM match_losses LEFT JOIN match_wins ON match_wins.player_id = match_losses.player_id
                            ORDER BY match_wins.num_wins;

-- Builds a paired ranking system, where the two 0s are the top two players, two 1s are the next top players, two 2s are the following top players, etc...
CREATE VIEW rankings AS SELECT player_id,
                               player_name,
                               (ROW_NUMBER() OVER (ORDER BY num_wins DESC) -1) / 2 AS ranking
                        FROM players LEFT JOIN match_totals ON players.id = match_totals.player_id;

-- Joins each row from the above rankings view on the ranking using a self join. To avoid duplication, player 1's id will always be less than player 2s id.
CREATE VIEW pairings AS SELECT r1.player_id AS player_id_1,
                               r1.player_name AS player_name_1, 
                               r2.player_id AS player_id_2,
                               r2.player_name AS player_name_2
                        FROM rankings r1 JOIN rankings r2 ON r1.ranking = r2.ranking
                        WHERE r1.player_id < r2.player_id;
