import sys
import json
from scipy import stats
import numpy as np
import pandas as pd

termtype_lst = ["religious", "anxiety", "optimistic", "terror"]
other_partynames = {'Green Party': 'Green',
                    'Forces et Démocratie':'Bloc Québécois',
                    'GPQ (ex-Bloc)':'Bloc Québécois',
                    'Québec debout':'Bloc Québécois', 
                    'Progressive Conservative': 'Conservative',
                    'Canadian Alliance': 'Conservative',
                    'Reform': 'Conservative',
                    }

def convert_to_dataframe(data):
    """
    Read count json data then make following dataframe:

        name party riding optimistic anxiety terror
    0
    1
    2
    ...

    where optimistic, anxiety and terror corresponds to their normalized frequency.
    
    """ 

    
    entries= []
    for each_mp in data:
        each_entry = data[each_mp]
        each_entry["name"] =  each_mp

        # merge parties
        party_name = each_entry["party"]
        if party_name in other_partynames:
            each_entry["party"] = other_partynames[party_name]

        # calculate normalized frequencies
        for termtype in termtype_lst:
            each_entry[termtype] = each_entry[termtype]/each_entry['total words']
        
        entries.append(each_entry)
    
    mp_df = pd.DataFrame(entries)
    mp_df = mp_df.set_index("name")

    return mp_df



def linear_regression(df, scope, attribute_x, attribute_y):
    """
    return linear regression slope and p-value between
    attribute_x, and attribute_y.
    
    scope determines which data to compute on.
    """
    if scope == "entire":
        mp_df = df
    else:
        mp_df = df.loc[df["party"] == scope]
        
    x = np.array(mp_df[attribute_x])
    y = np.array(mp_df[attribute_y])

    
    slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)

    print("slope: {} ".format(slope))
    print("p_value: {} ".format(p_value))



def main(data_path):

    data = json.load(open(data_path))

    mp_df = convert_to_dataframe(data)

    # export to csv just for reference.
    # mp_df.to_csv("./processedData/mps_freq_l_20.csv")

    # calculate linear regression to compare correlation.
    linear_regression(mp_df, "Bloc Québécois", "terror", "religious")

    
    

    

    
    

    

if __name__ == "__main__":
    

    if len(sys.argv) != 2 :
        print("Error: only one argument expected.")
        sys.exit(1)
    
    data_path = sys.argv[1]
    main(data_path)
