from slackclient import SlackClient
import settings, time, pandas as pd
from contextlib import contextmanager

bot_name = settings.slack['bot_name']
slack_client = SlackClient(settings.slack['token'])

BOT_ID = settings.slack['BOT_ID']

DM = settings.dnd["DM"]
lootmaster = settings.dnd["lootmaster"]
AT_BOT = "<@" + BOT_ID + ">:"
im_list = {}
members = {}


@contextmanager
def retrieve():
    try:
        store = pd.HDFStore('data.h5')
        yield store
    finally:
        store.close()


class loot:
    def _balance(user):
        """
        *_balance*
        Internal helper method to calculate balance.
        """
        money = data.get_balance(user)
        return "Balance for *{}*\n{:,}gp  {:,}sp  {:,}cp".format(user,money[gp],money[sp],money[cp])
    def add_item(command,channel,member):
        """
        *ADD_ITEM*
        _*NOT YET IMPLEMENTED*_
        Allows the DM or lootmaster to directly add an item to a player.
        """
        return "This isn't implemented yet."
    def alter_funds(command,channel,member):
        """
        *ALTER*
        _*NOT YET IMPLEMENTED*_
        Allows the DM or lootmaster to directly adjust balance up or down
        """
        if(members[channel] != DM):
            return "*HEY! STOP THAT! YOU'RE NOT THE DM!*"
        return "This isn't implemented yet."
    def approve(command,channel,member):
        """
        *APPROVE*
        Allows the DM to approve a transaction:
        *@lootbot: approve* _id_

        Optionally, the DM can override the amount with:
        *@lootbot: approve* _id_ _amount_ 

        If the DM chooses, he can also override the default denomination of gp with:
        *@lootbot: approve* _id_ _amount_ _denomination_
        
        """
        if(members[channel] != DM):
            return "*HEY! STOP THAT! YOU'RE NOT THE DM!*"
        com = command.split()
        if (len(com) < 2):
            return "ID of transaction required."
        elif( len(com) == 3):
            return loot._transaction('approved',id=com[1],amount=com[2])            
        elif(len(com)>3):
            return loot._transaction("approved",id=com[1],amount=com[2],coin=com[3])
        return loot._transaction('approved',id=com[1])
    def deny(command,channel,member):
        """
        *DENY*
        Allows the DM to deny a transaction:
        *@lootbot: deny* _id_
        """
        if(members[channel] != DM):
            return "*HEY! STOP THAT! YOU'RE NOT THE DM!*"
        com = command.split()
        if (len(com) < 2):
            return "ID of transaction required."
        return loot._transaction('denied',id=com[1])
    def balance(command,channel,member,*args,**kwargs):
        '''
        *BALANCE*
        Prints out the amount of money available for use by the player.

        The DM and lootmaster can check the loot of any player. The syntax for this is 
        *@lootbot: balance* _user_
        '''
        user = members[member]
        if((user == DM or user == lootmaster)):
            coms = command.lower().split()
            if(len(coms) > 1):
                if (coms[1] in members.values()):
                    return loot._balance(coms[1])
                else:
                    return loot.balance.__doc__
        return loot._balance(user)
    def purchase(command,channel,user,*args,**kwargs):
        """
        *PURCHASE*
        Allows a user to purchase an item and have the funds deducted from their balance.
        """
        item = command.split(sep=None,maxsplit=1)[1]
        amount, coin = data.item_metadata(item)
        return loot._transaction('purchase',user=user,item=item,amount=amount,coin=coin)
    def sell(command,channel,user,*args,**kwargs):
        """
        *SELL*
        Allows a user to sell an item and have the funds added to their balance.
        """
        item = command.split(sep=None,maxsplit=1)[1]
        amount, coin = data.item_metadata(item)
        amount = amount * 0.5
        return loot._transaction('sell',user=user,item=item,amount=amount,coin=coin)
    def help(command,channel,user,*args,**kwargs):
        """
        Kinda redundant to call help on help, don't you think?
        """
        split = command.lower().split()
        com = split[0]
        response = ""
        if (len(split) > 1):
            if(hasattr(loot,split[1])):
                return "Help for the *{}* command:\n{}".format(split[1],getattr(loot,split[1]).__doc__)
            else:
                response = "*{}* is not a valid command.\n".format(split[1])
        response += ', '.join([c for c in dir(loot) if not c.startswith("_")])
        response += "\nType *help* followed by one of the commands above to get more info."
        return response
    def _transaction(transaction,user=None,item=None,id=None,amount=None,coin='gp',*args,**kwargs):
        '''
        *Transaction*
        Internal helper function designed to ask the DM for approval on purchases and sales.
        '''
        if((transaction == 'purchase') or (transaction == 'sell')):
            id = data.add_transaction(user,item)
            message = """
            *APPROVAL NEEDED*
            {} wants to {}: {} for {:,}{}. Type @lootbot: *approve* or *deny* {}
            """.format(user,transaction,item,id,amount,coin)
            c = ''.join([k for k,v in members if v == DM])
            slack_client.api_call("chat.postMessage", channel=c,
                            text=message, as_user=True)
            return '{} of {} pending approval.'.format(transaction, item)
        elif((transaction == 'approved') or transaction == 'denied'):
            user,t,item = getattr(data,transaction)(id,amount)
            message = """
            {} *{}* your {} of *{}* for {:,}{}.
            =========
            *Itemlist:* {}
            =========
            {}
            """.format(DM,transaction,t,item,amount,coin,data.itemlist(user),loot._balance(user))
            c = ''.join([k for k,v in members if v == user])
            slack_client.api_call("chat.postMessage", channel=c,
                            text=message, as_user=True)
            return "You {} {}'s {} of {} for {:,}{}.".format(transaction,user,t,item,amount,coin)

        return None
    def hi(command,channel,user,*args,**kwargs):
        return "Hi, {}!".format(user)

class data:
    def itemlist(user):
        items = []
        with retrieve() as f:
            df = f['player_items']
            filtered = df[df['player'] == user]
            filtered['item'].map(lambda x: items.append(x))
        return ', '.join(items)
    def item_metadata(item):
        amount = None
        coin = None
        with retrieve() as f:
            df = f['itemlist']
            amount = df[df['item'] == item]['amount']
            coin = df[df['item'] == item]['coin']
        return amount, coin

    def get_balance(user):
        coins = {}
        with retrieve() as f:
            df = f['balances']
            filtered = df[df['player'] == user]
            group = filtered[['amount','coin']].groupby('coin').sum()
            for i in group.index:
                coins[i] = group['amount'][i]
        return coins

    def add_transaction(user,item,amount):
        with retrieve() as f:
            # TODO: Add amount retrieval from item_metadata.
            df = f['transactions']
            i = len(df)
            df.loc[i] = [user,item,amount,coin,'pending',pd.datetime.now()]
            f['transactions'] = df
        return i

    def approved(id,amount):
        item = ""
        user = ""
        t = ""
        
        # Flag the item as approved.
        with retrieve() as f:
            df = f['transactions']
            df['status'][id] = 'approved'
            df['DM_timestamp'][id] = pd.datetime.now()
            item = df['item'][id]
            user = df['player'][id]
            t = df['transaction'][id]
            if(not amount):
                amount = df['amount'][id]
        # Debit the amount from the player's account
        with retrieve() as f:
            df = f['balances']
            # TODO: determine format of balance "table"
            df.loc[len(df)] = [user,amount,coin,pd.datetime.now()]
            f['balances'] = df
        # Add the item to the player's itemlist
        with retrieve() as f:
            df = f['player_items']
            # TODO: determine format of player_items "table"
            df.loc[len(df)] = [user,item,pd.datetime.now()]
            f['player_items'] = df
        return user,t,item

    def denied(id,amount):
        item = ""
        user = ""
        t = ""
        with retrieve() as f:
            df = f['transactions']
            df['status'][id] = 'denied'
            df['DM_timestamp'][id] = pd.datetime.now()
            item = df['item'][id]
            user = df['player'][id]
            t = df['transaction'][id]
        return user,t,item
    

def handle_command(command, channel, user):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *help* command to find other commands."
    if(len(command) > 0):
        com = command.lower().split()[0]
    if (len(user) > 0):
        mem = members[user]
    if(com.startswith("hi") or com.startswith("help")):
        response = getattr(loot,com)(command,channel,user)
    elif (channel not in im_list.keys()):
        response = "Not sure what you want, {}. Try sending me a direct message!".format(mem)
    elif (hasattr(loot,com)):
        print(com)
        response = getattr(loot,com)(command,channel,user)
        print(response)
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                #print(output.keys())
                # output keys = 'team', 'text', 'type', 'channel', 'user', 'ts'
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], output['user']
    return None, None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        users = slack_client.api_call("users.list")
        for user in users['members']:
            members[user['id']] = user['name']
        ims = slack_client.api_call("im.list")
        for im in ims['ims']:
            im_list[im['id']] = im['user']
        print("LootBot connected and running!")
        #print("MEMBERS:\n{}\n\nIM_LIST:\n{}".format(members,im_list))
        while True:
            command, channel,user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel,user )
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")