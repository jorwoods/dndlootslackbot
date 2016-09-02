import pandas as pd
import os



if(not os.path.exists("data.h5") ):
    with pd.HDFStore("data.h5") as f:
        f['transactions'] = pd.DataFrame(columns=['player','item','amount',
            'coin','status','timestamp','DM_timestamp'])
        f['player_items'] = pd.DataFrame(columns=['player','item','timestamp'])
        f['balances'] = pd.DataFrame(columns=['player','amount','coin','timestamp'])

        # Load and prep the itemlist
        df = pd.read_excel("itemlist.xlsx")
        df['item'] = df['Name']
        df['rarity'] = df['Rarity']
        df['attuned'] = df['attunement?']
        f['itemlist'] = df[['item','amount','coin','rarity','page','attuned']]
        del(df)
    pass
