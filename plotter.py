import sys
import matplotlib.pyplot as plt
import json
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import pandas as pd
import datetime

# key: parties splitted and lasted under 5 years,
#       or party names designated in alternative name.
# value: parties either splitted from,
#         or party names more conventional.
other_partynames = {'Green Party': 'Green',
                    'Forces et Démocratie':'Bloc Québécois',
                    'GPQ (ex-Bloc)':'Bloc Québécois',
                    'Québec debout':'Bloc Québécois',
                    'Progressive Conservative': 'Conservative',
                    'Canadian Alliance': 'Conservative',
                    'Reform': 'Conservative',
                    }

color_dict = {"Conservative": "#000080", "Liberal": "red", "New Democratic Party":"magenta",
                    "Bloc Québécois":"yellow", "Green":"green", "Independent":"#C0C0C0"} # //-/

termtype_lst = ["religious", "anxiety", "optimistic", "terror"]



def count_party(data, term_type):
    """
    data: data loaded from mps_count.json
    term_type: type of terms to count e.g. 'religious', 'anxiety', etc

    termAvgCount_dict = {party: <normalised count of words>}
    """

    def merge_similar_parties(termCount_dict, totalWords_count):
        """
        Merge similar parties which are:
            - parties that lasted less than 5 years.
                e.g. 'Forces et Démocratie', 'GPQ (ex-Bloc)',
                            'Québec debout' -> Bloc Québécois'
            - parties designated under different word for
                e.g. 'Green Party' -> 'Green'

        """
        merged_termCounts = {}
        merged_totalWords = {}

        for each_party in termCount_dict:
            if each_party not in other_partynames:
                merged_termCounts[each_party] = termCount_dict[each_party]
                merged_totalWords[each_party] = totalWords_count[each_party]

        for each_party in termCount_dict:
             if each_party in other_partynames:
                # to be merged party name.
                other_name = other_partynames[each_party]

                merged_termCounts[other_name] += termCount_dict[each_party]
                merged_totalWords[other_name] += totalWords_count[each_party]

        return merged_termCounts, merged_totalWords


    termCount_dict = {}
    totalWords_count = {}

    for name in data:
        party = data[name]["party"]
        try:
            termCount_dict[party] += data[name][term_type]
            totalWords_count[party] += data[name]['total words']
        except:
            termCount_dict[party] = data[name][term_type]
            totalWords_count[party] = data[name]['total words']

    merged_counts, merged_total = merge_similar_parties(termCount_dict, totalWords_count)

    for each_party in merged_counts:
        merged_counts[each_party] = merged_counts[each_party]/merged_total[each_party]

    return merged_counts


def plot_party(term_count_dict, term_type):

    mps_pf = [] # tuples of party and frequency
    for pf_tup in term_count_dict.items():
            mps_pf.append(pf_tup)

    mps_pf.sort(key=lambda x: x[1], reverse=True)

    # (2009-2018)'
    mytitle = 'Frequency of ' + 'Religious ' + ' Words by Party' + ' (1999-2018)'
    plt.title(mytitle)
    plt.ylabel('Frequency normalized')
    plt.xlabel('Party')

    X,Y = zip(*mps_pf)

    bars = plt.bar(range(len(X)), Y, 0.6)
    plt.xticks(range(len(X)), X)

    for i, bar in enumerate(bars):
        try:
            bar.set_color(color_dict[X[i]])
        except:
            bar.set_color('black') # default color

    # plt.tight_layout()
    # plt.savefig('l_10_reli_party')
    plt.show()


def count_mps(data, term_type):
    """
    Count term_type and cluster them by parties.
    {<party>: {<name>: <normalized frequency>}}
    """

    def merge_similar_parties(unmerged_indiv_count):

        """
        Merge similar parties which are:
            - parties that lasted less than 5 years.
                e.g. 'Forces et Démocratie', 'GPQ (ex-Bloc)',
                            'Québec debout' -> Bloc Québécois'
            - parties designated under different word for
                e.g. 'Green Party' -> 'Green'
        """
        merged_indiv_count = {}
        for party_name in unmerged_indiv_count:
            if party_name not in other_partynames:
                merged_indiv_count[party_name] = unmerged_indiv_count[party_name]

        for party_name in unmerged_indiv_count:
            if party_name in other_partynames:
                other_name = other_partynames[party_name]
                merged_indiv_count[other_name].update(unmerged_indiv_count[party_name])

        return merged_indiv_count


    indiv_count = {}

    for name in data:
        party = data[name]["party"]

        try:
            indiv_count[party][name] = data[name][term_type]/data[name]['total words']
        except:
            indiv_count[party] = {}
            indiv_count[party][name] = data[name][term_type]/data[name]['total words']

    merged_indiv_count = merge_similar_parties(indiv_count)
    # print("Number of Mps: {}".format(mps_count))

    return merged_indiv_count


def plot_mps(indiv_mps_count, term_type):
    """
    Plot frequeny of usage by mps, then cluster them by their parties for
    better insight on how frequency is distributed.

    {party: {<name>: frequency}}

    Color:
        #000080: Blue
        #C0C0C0: Silver

    """

    mps_nfp = [] # name, frequency party
    mps_count = 0

    for party in indiv_mps_count:

        # //-/
        if party in ["Conservative", "New Democratic Party", "Liberal"]:

            mps_count += len(indiv_mps_count[party])

            for name, freq in indiv_mps_count[party].items():
                mps_nfp.append((name, freq, party))

    sorted_mps_nfp = sorted(mps_nfp, key=lambda tup: tup[1])
    print(sorted_mps_nfp[-3:])

    X,Y,R = zip(*sorted_mps_nfp)

    # (2009-2018)
    mytitle = 'Frenquency of Religious Words by Members of Parliaments (1999-2018)'
    plt.title(mytitle)
    plt.ylabel('Frequency of Religious Words')
    plt.xlabel('Individual MPs')

    # patches
    conservative_patch = mpatches.Patch(color=color_dict['Conservative'], label='Conservative')
    liberal_patch = mpatches.Patch(color=color_dict['Liberal'], label='Liberal')
    ndp_patch = mpatches.Patch(color=color_dict['New Democratic Party'], label='New Democratic Party')
    bq_patch = mpatches.Patch(color=color_dict['Bloc Québécois'], label='Bloc Québécois')
    green_patch = mpatches.Patch(color=color_dict['Green'], label='Green')
    ind_patch = mpatches.Patch(color=color_dict['Independent'], label='Independent')

    plt.legend(
                    handles=[conservative_patch, liberal_patch, ndp_patch,
                        bq_patch, green_patch, ind_patch
                        ])

    bars = plt.bar(range(len(X)), Y, 0.6, color='blue')

    for i, bar in enumerate(bars):
        try:
            bar.set_color(color_dict[R[i]])
        except:
            bar.set_color('black') # default color

    # plt.tight_layout()
    print("Number of Mps: {}".format(mps_count))
    plt.show()


def count_by_date(data):

    count_dict = {}

    for each_date in data:

        count_dict[each_date] = {}

        for term_type in termtype_lst:
            try:
                term_dict =  data[each_date][term_type]
                count_dict[each_date][term_type] = sum(term_dict.values())
            except:
                count_dict[each_date][term_type] = 0




    return count_dict


def plot_chronologically(date_count_dict, term_type):
    """
    Plot frequeny of usage by mps, then cluster them by their parties for
    better insight on how frequency is distributed.

    {party: {<name>: frequency}}

    Color:
        #000080: Blue
        #C0C0C0: Silver

    """

    date_count_lst = [] # date, count

    for date_str in date_count_dict:
        term_count = date_count_dict[date_str][term_type]

        date_count_lst.append((datetime.datetime.strptime(date_str, "%Y-%m-%d"), term_count))

    # print(date_count_lst)
    sorted_tup_lst = sorted(date_count_lst, key=lambda dc_tup: dc_tup[0])
    date_count_lst = list(map(lambda each_tup: (datetime.datetime.strftime(each_tup[0],"%Y-%m-%d"), each_tup[1]), sorted_tup_lst))


    X,Y = zip(*date_count_lst)

    # (2009-2018)
    mytitle = "Count: " + term_type +  " words by Date Over Time(1999-2018)"
    plt.title(mytitle)
    plt.ylabel('Count of Terror Words')
    plt.xlabel('Dates in Chronological Order')

    xscale_full_lst = list(map(lambda dc_tup: dc_tup[0], date_count_lst))

    xscale_label = []
    i = 0
    while i < len(xscale_full_lst):
        if i % 200 == 0:
            xscale_label.append(xscale_full_lst[i])
        i += 1

    # print(xscale_label)
    plt.xticks(range(0, len(date_count_lst), 200), xscale_label)
    plt.xticks(rotation=45, fontsize=8)

    bars = plt.plot(range(len(X)), Y, color='blue', linewidth=0.2)


    plt.tight_layout()
    plt.show()


def main(data_path):
    data = json.load(open(data_path))
    # PLOTTING BY PARTY
    # party_reli_count = count_party(data, 'religious')
    # print(sorted(party_reli_count.items(), key=lambda x: x[1], reverse=True))
    # print(party_reli_count.keys())
    # plot_party(party_reli_count, 'religious')

    # PLOT MY MPS CLUSTERED BY PARTIES

    # count_by_parties = count_mps(data, 'terror')
    # mp_freq_tup_lst = []
    # for each_party in count_by_parties:
    #     mp_freq_tup_lst += count_by_parties[each_party].items()

    # mp_freq_tup_lst.sort(key=lambda x: x[1], reverse=True)
    # # count_by_parties = list(map(lambda x: (x, len(mps_reli_count[x])) , mps_reli_count.keys()))
    # print(mp_freq_tup_lst[:5])
    # # # plot_mps(mps_reli_count, 'religious')

    # prints out the most frequently used words

    top_five = ['Susan Truppe', 'Glen Motz', 'Roxanne James', 'Anju Dhillon', 'Leona Aglukkaq']
    for each_name in top_five:
        reli_term_count = data[each_name]['terror']
        print(each_name)
        sorted_terms = sorted(reli_term_count.items(), key=lambda x: x[1], reverse=True)
        formatted = ""
        for each_tuple in sorted_terms:
            formatted += each_tuple[0] + ': ' + str(each_tuple[1]) + ', '
        formatted = formatted[:-2] + '.'
        print(formatted)


    # PLOTTING IN CHRONOLGICAL ORDER
    # date_count = count_by_date(data)
    # plot_chronologically(date_count, 'terror')



if __name__ == "__main__":

    if len(sys.argv) != 2 :
        print("Error: only one argument expected.")
        sys.exit(1)

    data_path = sys.argv[1]
    main(data_path)
