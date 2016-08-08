# DnD loot slackbot
This bot is designed for my dungeons and dragons group. The idea is to simplify how our group can check their item list, cash balance, etc. 

## Intended features:
* Query bot for balance with "balance"
  * balance should be displayed in gp, sp, and cp
* Query bot for items with "item list"
  * Details of items that should be displayed TBD
* Purchase items with "buy \<item name\>"
  * Balanced should be posted along with purchase confirmation
* Sell items with "sell \<item name\>"
* Wishlist item with "wishlist \<item name\>"
  * User should be notified when they have enough cash to buy wishlist item. Notification should only happen once.
  * Should wishlist items be displayed along with balance when balance queried?
* "help" query should display the commands. "help \<command\>" should display more detail about the command.

## ToDo:
* Implement the above
* Decide on datasource:
  * Google Docs?
  * Postgres?
  * DynamoDB?