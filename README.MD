# DnD loot slackbot
This bot is designed for my dungeons and dragons group. The idea is to simplify how our group can check their item list, cash balance, etc. 

## Intended features:
* Query bot for balance with "balance"
  * balance should be displayed in gp, sp, and cp. (Ignoring electrum and platinum)
* Query bot for items with "item list"
  * Details of items that should be displayed TBD
* Purchase items with "buy \<item name\>"
  * Balance should be posted along with purchase confirmation and item price
* Sell items with "sell \<item name\>"
  * Balance should be posted along with sale confirmation and item price
* Wishlist item with "wishlist \<item name\>"
  * User should be notified when they have enough cash to buy wishlist item. Notification should only happen once.
  * Should wishlist items be displayed along with balance when balance queried?
* "help" query should display the commands. "help \<command\>" should display more detail about the command.

## ToDo:
* Implement the above
=======
* DM and loot master should be able to add/remove items/funds without impacting existing balances. Others should not.
* Add option for DM approval of purchases/sales. This will need a threshold variable, settable by DM.
* DM will need purchase/sale ability over all characters.
* Users should be notified when their balance changes: by how much, why, and the new balance.
* Users should not be able to buy items that would put them under 0.

---
## Potential long term niceties
* Users lending each other money. Loans should appear in balance requests (both debtor and creditor), how much and to whom.
  * Does DM need notification of loans?
 
---
## Design decisions
* Data source for now will likely be HDF5. A project at this small scale will not benefit meaningfully from a database back end.
* Interactions with slack should be asynchronous to not block other requests from occurring.