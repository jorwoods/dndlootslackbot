import pandas as pd
import os



if(not os.path.exists("data.h5") ):
    with pd.HDFStore("data.h5") as f:
        f['transactions'] = pd.DataFrame(columns=['player','item','amount',
            'coin','status','timestamp','DM_timestamp'])
        f['player_items'] = pd.DataFrame(columns=['player','item','timestamp'])
        f['balances'] = pd.DataFrame(columns=['player','amount','coin','timestamp'])
        f['itemlist'] = pd.DataFrame(columns=['item',
            'amount','coin','rarity','consumable'])
    pass
