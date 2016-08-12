from slackclient import SlackClient
import settings, time, pandas as pd

bot_name = settings.slack['bot_name']
slack_client = SlackClient(settings.slack['token'])

BOT_ID = settings.slack['BOT_ID']

DM = settings.dnd["DM"]
lootmaster = settings.dnd["lootmaster"]
AT_BOT = "<@" + BOT_ID + ">:"
im_list = {}
members = {}
#funds = pd.DataFrame

class loot:
    def _balance(user):
        """
        *_balance*
        Internal helper method to calculate balance.
        """
        #money = funds[(funds.name == user)]['money']
        money = 123456789
        gp = money // 100
        sp = (money % 100) // 10
        cp = money % 10
        return "Balance for *{}*\n{:,}gp  {}sp  {}cp".format(user,gp,sp,cp)
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
        pass
    def sell(command,channel,user,*args,**kwargs):
        """
        *SELL*
        Allows a user to sell an item and have the funds added to their balance.
        """
        pass
    def help(command,channel,user,*args,**kwargs):
        """
        Kinda redundant to call help on help, don't you think?
        """
        split = command.lower().split()
        com = split[0]
        response = ""
        if (len(split) > 1):
            if(hasattr(loot,split[1])):
                return "Help for the {} command:\n{}".format(split[1],getattr(loot,split[1]).__doc__)
            else:
                response = "*{}* is not a valid command.\n".format(split[1])
        response += ', '.join([c for c in dir(loot) if not c.startswith("_")])
        response += "\nType *help* followed by one of the commands above to get more info."
        return response
    def hi(command,channel,user,*args,**kwargs):
        return "Hi, {}!".format(user)

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
    if(channel not in im_list.keys() and (com.startswith("hi") or com.startswith("help"))):
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
        while True:
            command, channel,user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel,user )
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")