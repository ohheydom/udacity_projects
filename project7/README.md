# Farkle

## Introduction

Farkle is a dice game played by two or more players in which each player attempts to reach a predetermined value by rolling and banking certain dice. The players take turns until one player reaches the mark, where the remaining player has one more opportunity to catch up to the player. If he/she surpasses the original player that beat the winning total, that player wins. Otherwise, the original player to surpass the winning total wins.

## Scoring

A player scores when he/she decides to bank the dice that he/she has collected.

The player can choose to bank his/her current total or take a chance and re-roll the unselected dice. The turn ends when the player either banks his/her cumulative total or farkles. A farkle occurs when the roll contains no scoring die. The cumulative total is then wiped out and the player scores 0.

### Scoring System

Individual 1s are worth 100 points each.
Individual 5s are worth 50 points each.

All other values are not worth anything unless there are three or more.

Three of a kind:
1: 1000
2: 200
3: 300
4: 400
5: 500
6: 600

Four of a kind:
All: 1000

Five of a Kind:
All: 2000

Six of a kind:
All: 4000

Scores are computed for each roll. So for instance, if you roll:

```
1,1,4,4,6,6
```
You can only save the 1s because two 4s and two 6s are not worth anything. You cannot rollover values to your next roll.

For further information, please visit the [Wikipedia entry](https://en.wikipedia.org/wiki/Farkle).

## Instructions

Change to the app directory and run:

```
dev_appserver.py app.yaml worker.yaml
```

You can then visit the api explorer in your browser from:

```
http://localhost:8000/_ah/api/explorer
```
To play:
* Create two users via the new\_user endpoint.
* Create a new game via the new\_game endpoint, selecting the usernames of the two players you created and a winning score value. To keep the game short, select a low value like 500.

* Roll the dice via the roll\_dice endpoint
  * Look at the response and determine the indices of the dice you wish to save. Copy the game id (urlsafe\_key) to your clipboard
* Using the save\_dice endpoint, input the game id that you saved and the indices of the dice you wish to save.
  * If you bank, play moves onto the next player and the total you collected from the current turn gets added to your score.
  * If you choose to not bank your current score, the game will reroll the remaining dice.
    * If there are playable dice (1s, 5s, or three or more of any dice), look at the response and again determine the dice you wish to save and if you want to bank.
    * If there are no playable dice, you farkle, lose the points collected on the current turn, and play moves onto the next player.
  * If there are 0 remaining dice after saving, you have hot dice and can continue rolling starting with a new set of 6 dice.
* Repeat

* Endgame
  * An endgame occurs when one player has banked a score above the winning total.
  * The next player then has a chance to surpass the other player's score.
  * If he/she does so, he/she wins. Otherwise, the other player wins.

## Api Endpoints

* **new\_user**
  * Path: `new\_user`
  * Method: POST
  * Parameters: name, email
  * Returns: Message confirmation
  * Description: Creates a new user based on a unique name. The endpoint will raise a ConflictException if the user already exists.

* **new\_game**
  * Path: `new\_game`
  * Method: POST
  * Parameters: player\_one\_name, player\_two\_name, winning\_total
  * Returns: GameForm with game state
  * Description: Creates a new game with two unique players. Both players must exist in the database or the endpoint will raise a NotFoundException.

* **get\_game**
  * Path: `game/{urlsafe\_key}`
  * Method: GET
  * Parameters: urlsafe\_key
  * Returns: GameForm with the current game state
  * Description: Returns the game state. Raises a NotFoundException if game does not exist.

* **delete\_game**
  * Path: `game/{urlsafe\_key}/delete`
  * Method: DELETE
  * Parameters: urlsafe\_key
  * Returns: Message confirmation
  * Descriptions: Deletes an incomplete game. If the game is already completed, the endpoint returns a BadRequestException. If game is not found, it raises a NotFoundException.

* **roll\_dice**
  * Path: `game/{urlsafe\_key}/roll\_dice`
  * Method: PUT
  * Parameters: urlsafe\_key
  * Returns: GameForm
  * Description: Rolls the dice and inserts the values into the database

* **save\_dice**
  * Path: `game/{urlsafe\_key}/save\_dice`
  * Method: PUT
  * Parameters: urlsafe\_key, indices, bank
  * Returns: GameForm
  * Description: Saves the indices of the dice that a user wishes to retain. The player can choose to bank the score pertaining to those specific dice and the previously saved dice or continue rolling.

* **get\_user\_games**
  * Path: `user/{username}/games`
  * Method: GET
  * Parameters: username
  * Returns: GameForms
  * Descriptions: Returns all the games that a user is currently playing.

* **get\_user\_rankings**
  * Path: `user\_rankings`
  * Method: GET
  * Parameters: None
  * Returns: UserRankingsForms
  * Descriptions: Returns the rankings of all users in the database in descending order by rank. Rank is determined by winning percentage.

* **get\_game\_history**
  * Path: `game/{urlsafe\_key}/history`
  * Method: GET
  * Parameters: urlsafe\_key
  * Returns: GameHistoryForm
  * Descriptions: Returns the scoring history of both players from a specific game

All methods that require a game id will raise a NotFoundException if the game does not exist.

## Models

* **User** - Stores a unique username and email address.
* **Game** - Stores each unique game.

## Forms

* **GameForm** - Represents the game's state.
* **GameHistoryForm** - Shows the moves of game.
* **NewGameForm** - Assists in creating a new game.
* **NewUserForm** - Used to create a new user.
* **UserRankingsForm** - Displays the rankings.
* **StringMessage** - Returns a general message

## PushQueue

When a user has finished his/her move, the next player is sent a reminder e-mail that it is his/her turn. A User may choose to opt out of these e-mails via the database property `email_me`. If set to false, the user will not be emailed.
