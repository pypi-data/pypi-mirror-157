from collections import defaultdict as _defaultdict
from bs4 import BeautifulSoup as _BeautifulSoup
import pandas as _pd
import numpy as _np
import datetime as _datetime
import requests as _requests
# import lxml.html as _lh
from sklearn import linear_model as _linear_model
import matplotlib as _matplotlib
import matplotlib.pyplot as _plt
# from matplotlib.ticker import AutoMinorLocator as _AutoMinorLocator


# ----------------------------------------------------
# These are deprecrated functions to extract the data
# ----------------------------------------------------
def _get_mendota_soup():
    """**DEPRECATED** gets soup object"""
    url = 'https://www.aos.wisc.edu/~sco/lakes/Mendota-ice.html'
    r = _requests.get(url)
    html = r.text
    return _BeautifulSoup(html, "html.parser")


def _get_headers(soup=None):
    """**DEPRECATED** extracts headers"""
    return [val for val in soup.find('table').stripped_strings][0:4]


def _get_data_dict(soup=None, headers=None):
    """**DEPRECATED** gets data from dictionary"""
    # initate a dictionary to store data
    def_dict = _defaultdict(list)

    for match in soup.find_all('tr'):
        col_list = []  # will store all the colums
        for font in match.find_all('font'):
            tmp_list = [data for data in font.stripped_strings]

            # puts column into temporary list based on length
            if len(tmp_list) > 0:
                col_list.append(tmp_list)

        # put first half in dict
        for enum, col in enumerate(col_list[0:4]):
            def_dict[headers[enum]].extend(col)

        # put second half in def_dict
        for enum, col in enumerate(col_list[4:]):
            def_dict[headers[enum]].extend(col)

    return dict(def_dict)


def _dict_to_df(dict_=None):
    """**DEPRECATED** converts dictionary to dataframe"""
    return _pd.DataFrame.from_dict(dict_)


# ----------------------------------------------------
# parse url using xml
# ----------------------------------------------------
"""
def _parse_url_xml():
    # gets the data from url and extracts it
    # read html
    url = 'https://www.aos.wisc.edu/~sco/lakes/Mendota-ice.html'
    r = _requests.get(url)

    # Parse the html, returning a single element/document.
    doc = _lh.fromstring(r.text)

    # traverse document to rows of each table
    targets = doc.xpath('//table//tr')

    # list to store all the columns
    entries = []

    target = targets[0]
    for target in targets:
        # gets the columns in each table
        subs = target.xpath('.//td')
        # this column is empty
        del subs[4]
        # puts each column entry in a list
        entries.extend([[s.strip() for s in sub.xpath('.//*/text()')]
                       for sub in subs])

    # some trailing empty elements needed to be removed before proceeding
    entries = [[list(filter(lambda x: x != "", entry))
                for entry in entries[r::4]] for r in range(4)]

    # unpack to the correct columns
    [Winter, Closed, Opened, Days] = [[x for list in entry for x in list]
                                      for entry in entries]

    # and now create a dataframe:
    final = _pd.DataFrame(list(zip(Winter, Closed, Opened, Days)),
                          columns=['WINTER', 'CLOSED', "OPENED", "DAYS"])

    return final
"""

# ----------------------------------------------------
# these functions clean the raw parsed dataset
# ----------------------------------------------------


def _fill_missing_values(df=None):
    """replace missing values with NaN"""
    # fills in rows where lake refroze in same season
    df['WINTER'].replace(to_replace='"', method='ffill', inplace=True)

    # use nan as the missing value
    for headr in ['DAYS', 'OPENED', 'CLOSED']:
        df[headr].replace(to_replace=['-', '--', '---'], value=_np.nan, inplace=True)

    return df.sort_values(by=['WINTER'])


def _change_dates_in_df(df=None):
    """adds year to the all dates"""
    for ind in range(len(df)):
        open_day_month = df['OPENED'][ind]
        close_day_month = df['CLOSED'][ind]
        year = int(df['WINTER'][ind][0:4])

        if isinstance(open_day_month, str):
            open_doy = int(_datetime.datetime.
                           strptime(f"{open_day_month}", '%d %b').strftime('%j'))
            # this is the lake opening before January of the next year
            if open_doy > 200:
                df['OPENED'][ind] = _datetime.datetime.\
                    strptime(f"{open_day_month} {year}", '%d %b %Y').\
                    strftime('%Y-%m-%d')

            # this is the lake opening the following year
            else:
                df['OPENED'][ind] = _datetime.datetime.\
                    strptime(f"{open_day_month} {year+1}", '%d %b %Y').\
                    strftime('%Y-%m-%d')
        else:
            df['OPENED'][ind] = _np.nan

        if isinstance(close_day_month, str):
            close_doy = int(_datetime.datetime.
                            strptime(f"{close_day_month}", '%d %b').
                            strftime('%j'))

            # this is the lake closing before January of the next year
            if close_doy > 200:
                df['CLOSED'][ind] = _datetime.datetime.\
                    strptime(f"{close_day_month} {year}", '%d %b %Y').\
                    strftime('%Y-%m-%d')

            # his is the lake closing the following year
            else:
                df['CLOSED'][ind] = _datetime.datetime.\
                    strptime(f"{close_day_month} {year+1}", '%d %b %Y').\
                    strftime('%Y-%m-%d')
        else:
            df['CLOSED'][ind] = _np.nan

    return df.sort_values(by=['WINTER'])


def _add_columns_to_dataset(df):
    """this adds new columns to the dataset"""
    d = _defaultdict(list)

    for winter in set(df['WINTER']):
        df_tmp = df.loc[df['WINTER'].isin([winter])]
        d['WINTER'].extend(df_tmp['WINTER'].iloc[[0]])
        d['CLOSED'].extend(df_tmp['CLOSED'].iloc[[0]])
        d['OPENED'].extend(df_tmp['OPENED'].iloc[[-1]])
        d['DAYS'].extend(df_tmp['DAYS'].iloc[[-1]])
        d['NUM_REFREEZES'].extend([len(df_tmp)])
        d['CLOSE_DAYS'].append(list(df_tmp['CLOSED']))
        d['OPEN_DAYS'].append(list(df_tmp['OPENED']))

    # sort the dict
    df = _pd.DataFrame.from_dict(dict(d))
    df = df.sort_values(by=['WINTER'])
    df.reset_index(drop=True, inplace=True)

    return df.sort_values(by=['WINTER'])


def _rename_columns(df):
    """sets the columns names"""
    df = df.rename(columns={'WINTER': 'season',
                            'CLOSED': 'iceon_date',
                            'OPENED': 'iceoff_date',
                            'DAYS': 'duration',
                            'NUM_REFREEZES': 'n_freezes',
                            'CLOSE_DAYS': 'n_iceon_dates',
                            'OPEN_DAYS': 'n_iceoff_dates', })
    return df


def _drop_nans(df):
    """removes rows where nan in all columns"""
    return df.dropna().reset_index(drop=True)


def _add_doy(df):
    doy_on = [val+365 if val <
              60 else val for val in _pd.to_datetime(df['iceon_date']).dt.dayofyear]
    doy_off = [val+365 if val <
               60 else val for val in _pd.to_datetime(df['iceoff_date']).dt.dayofyear]
    df = df.assign(iceon_doy=doy_on, iceoff_doy=doy_off)
    return df


def _correct_data_type(df):
    """corrects data types, ensure duration is an int"""
    df['duration'] = df['duration'].astype(int)
    return df


# ----------------------------------------------------
# load is where all the functions are strung together
# ----------------------------------------------------
def load():
    # old way to extract url deprecated
    soup = _get_mendota_soup()
    headers = _get_headers(soup)
    data_dict = _get_data_dict(soup, headers)
    df = _dict_to_df(data_dict)
    # df = _parse_url_xml()
    df_cleaned = _fill_missing_values(df)
    df_out = _change_dates_in_df(df_cleaned)
    df_fin = _add_columns_to_dataset(df_out)
    df_rename = _rename_columns(df_fin)
    df_dropped = _drop_nans(df_rename)
    df_doy = _add_doy(df_dropped)
    df_final = _correct_data_type(df_doy)
    return df_final


# ----------------------------------------------------
# plotting functions
# ----------------------------------------------------
def plot():
    df = load()

    # https://pythonguides.com/matplotlib-remove-tick-labels/
    fig = _plt.figure(figsize=(12, 6))
    gs = _matplotlib.gridspec.GridSpec(nrows=2, ncols=2,  width_ratios=[1, 1])
    ax0 = fig.add_subplot(gs[:, 0])
    ax1 = fig.add_subplot(gs[0, 1])
    ax2 = fig.add_subplot(gs[1, 1])

    ax = ax0

    x = df['season'].str.split('-').str[0].astype(float)
    y = df['duration']

    ax.scatter(x, y,
               marker='o',
               s=100,
               linewidth=3,
               color=(1, 1, 1, 1),
               edgecolor=[0.7, 0.7, 0.7],
               clip_on=False,
               zorder=2,
               )

    df2 = df.query("n_freezes == 2")

    x2 = df2['season'].str.split('-').str[0].astype(float)
    y2 = df2['duration']

    ax.scatter(x2, y2,
               marker='o',
               s=100,
               linewidth=3,
               color=(1, 1, 1, 1),
               edgecolor=[0.1, 0.1, 0.1],
               clip_on=False,
               zorder=2,
               )

    # linear regression
    regr_out = _linear_model.LinearRegression()
    regr_out.fit(x.values.reshape(-1, 1), y.values.reshape(-1, 1))

    # plot trend line
    ax.plot(x, regr_out.predict(x.values.reshape(-1, 1)), color='k', linewidth=3)

    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # set axis limits
    ax.set_ylim([0, 170])
    ax.set_xlim([1855, 2022])

    # tick marks
    ax.set_xticks(_np.arange(1860, 2021, 40))
    ax.set_yticks(_np.arange(14, 180, 14))

    # major/minor tick lines
    ax.grid(axis='y', which='major', color=[0.8, 0.8, 0.8], linestyle='-')

    # Labels
    ax.tick_params(axis='x', labelsize=16)
    ax.tick_params(axis='y', labelsize=16)

    # Turn off the display of all ticks.
    ax.tick_params(axis='both',
                   which='major',  # Options for both major and minor ticks
                   top='off',  # turn off top ticks
                   left='off',  # turn off left ticks
                   right='off',  # turn off right ticks
                   bottom='off',  # turn off bottom ticks
                   length=0,
                   )

    # Annotations
    title_str = """Duration of Ice Cover (Days)"""
    ax.set_title(title_str, fontsize=18, fontweight='bold', ha='center')

    ax = ax1

    x = df['season'].str.split('-').str[0].astype(float)
    y = df['duration']

    ax.plot(df['season'].str.split('-').str[0].astype(float),
            df['iceon_doy'], color='k', linewidth=2)

    ax.plot(df['season'].str.split('-').str[0].astype(float),
            df['iceoff_doy']+365, color=[0.5, 0.5, 0.5], linewidth=2)

    # Range ov axes
    ax.set_ylim([420, 492])
    ax.set_xlim([1855, 2022])

    yticks_start_end_step = (420+7, 500, 14)
    xticks_start_end_step = (1860, 2021, 40)

    # Turn off the display of all ticks.
    ax.tick_params(which='both',  # Options for both major and minor ticks
                   top='off',  # turn off top ticks
                   left='off',  # turn off left ticks
                   right='off',  # turn off right ticks
                   bottom='off')  # turn off bottom ticks

    # Remove x tick marks
    _plt.setp(ax.get_xticklabels(), rotation=0)

    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # major/minor tick lines
    ax.grid(axis='y', which='major', color=[0.8, 0.8, 0.8], linestyle='-')

    # Turn off the display of all ticks.
    ax.tick_params(axis='both',
                   which='major',  # Options for both major and minor ticks
                   top='off',  # turn off top ticks
                   left='off',  # turn off left ticks
                   right='off',  # turn off right ticks
                   bottom='off',  # turn off bottom ticks
                   length=0,
                   )

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    # Don't allow the axis to be on top of your data
    ax.set_axisbelow(True)
    ax.set_xticks(_np.arange(*xticks_start_end_step))
    ax.set_yticks(_np.arange(*yticks_start_end_step))

    ax.set_yticklabels([_datetime.datetime.fromordinal(doy).strftime('%b-%d')
                        for doy in range(*yticks_start_end_step)])

    # Labels
    ax.tick_params(axis='x', labelsize=16)
    ax.tick_params(axis='y', labelsize=16, labelleft=False, labelright=True)

    ax.xaxis.set_ticklabels([])

    # Annotations
    title_str = """Ice-off date"""
    ax.set_title(title_str, fontsize=18, fontweight='bold', ha='center')

    ax = ax2

    x = df['season'].str.split('-').str[0].astype(float)
    y = df['duration']

    ax.plot(df['season'].str.split('-').str[0].astype(float),
            df['iceon_doy'], color='k', linewidth=2)

    # Range ov axes
    ax.set_ylim([322, 400])
    ax.set_xlim([1855, 2022])

    yticks_start_end_step = (323+7, 400, 14)
    xticks_start_end_step = (1860, 2021, 40)

    # Turn off the display of all ticks.
    ax.tick_params(which='both',  # Options for both major and minor ticks
                   top='off',  # turn off top ticks
                   left='off',  # turn off left ticks
                   right='off',  # turn off right ticks
                   bottom='off')  # turn off bottom ticks

    # Remove x tick marks
    _plt.setp(ax.get_xticklabels(), rotation=0)

    # Hide the right and top spines
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    # major/minor tick lines
    ax.grid(axis='y', which='major', color=[0.8, 0.8, 0.8], linestyle='-')

    # Turn off the display of all ticks.
    ax.tick_params(axis='both',
                   which='major',  # Options for both major and minor ticks
                   top='off',  # turn off top ticks
                   left='off',  # turn off left ticks
                   right='off',  # turn off right ticks
                   bottom='off',  # turn off bottom ticks
                   length=0,
                   )

    # Only show ticks on the left and bottom spines
    ax.yaxis.set_ticks_position('left')
    ax.xaxis.set_ticks_position('bottom')

    # Don't allow the axis to be on top of your data
    ax.set_axisbelow(True)

    ax.set_xticks(_np.arange(*xticks_start_end_step))
    ax.set_yticks(_np.arange(*yticks_start_end_step))

    ax.set_yticklabels([_datetime.datetime.fromordinal(doy).strftime('%b-%d')
                        for doy in range(*yticks_start_end_step)])

    # Labels
    ax.tick_params(axis='x', labelsize=16)
    ax.tick_params(axis='y', labelsize=16, labelleft=False, labelright=True)

    # Annotations
    title_str = """Ice-on date"""
    ax.set_title(title_str, fontsize=18, fontweight='bold', ha='center')
