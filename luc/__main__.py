import argparse
import os
import re
import warnings
from pathlib import Path

import pandas as pd


SONGDIR = Path(os.getcwd())


def clean_string_col(col):
    try:
        out = col.str.strip().str.replace(' +', ' ', regex=True).str.lower()
    except AttributeError:
        out = col
        
    return out


def main(datedir, song_sheet_name, return_df=False):
    # compat
    DATEDIR = datedir
    SONG_SHEET_NAME = song_sheet_name
      
    pat = re.compile(
        r'^(?P<artist>.*) (?P<kpi>recordings\-\d{1,2}day|PW|YTD)(?: \(\d+\))?\.csv$')
    stat_sheets = []
    date_folder = DATEDIR
    for service_dir in date_folder.iterdir():
        if not service_dir.is_dir():
            continue
        for stat_sheet in service_dir.iterdir():
            if stat_sheet.name == '.ipynb_checkpoints':
                continue
            # get KPI and artist from file
            match = re.match(pat, stat_sheet.name)
            stats_df = pd.read_csv(stat_sheet)
            stats_df.columns = stats_df.columns.str.lower()
            stats_df = (stats_df
                  .rename(columns={'plays': 'streams'})[['song', 'streams']]
                  .assign(service=service_dir.name, **match.groupdict())
                  # .apply(clean_string_col)
                  .set_index(['artist', 'song', 'service', 'kpi'])
            )
            stat_sheets.append(stats_df)
    kpis = pd.concat(stat_sheets)
    # songs w same names like singles and albums, etc
    idx_names = kpis.index.names
    kpis = kpis.groupby(idx_names).sum()
    kpis_idx = kpis.drop(columns='streams')
    has = pd.util.hash_pandas_object(kpis)
    clean = kpis.drop(columns='streams').reset_index()
    kpis = kpis.reset_index().apply(clean_string_col).set_index(kpis.index.names)
    clean.index = pd.util.hash_pandas_object(kpis.index)
    
    song_sheet = pd.read_csv(DATEDIR/SONG_SHEET_NAME)
    song_sheet.columns = song_sheet.columns.str.strip().str.lower()
    song_sheet = song_sheet.dropna(how='all')
    song_sheet['artist'] = song_sheet['artist'].pad()
    song_sheet['song'] = song_sheet['include'].combine_first(song_sheet['exclude'])
    song_sheet = song_sheet.set_index(['artist', 'song'])
    song_sheet['action'] = song_sheet[['include', 'exclude']].notna().idxmax(axis=1)
    song_sheet = song_sheet.reset_index().melt(
        id_vars=('artist', 'song', 'action'),
        value_vars=('spotify', 'apple'),
        var_name='service',
        value_name='keep'
    )
    song_sheet = song_sheet.loc[song_sheet['keep'].notna()].drop(columns='keep')
    song_sheet = song_sheet.apply(clean_string_col)
    exclusions = song_sheet.loc[song_sheet['action']=='exclude']
    inclusions = song_sheet.loc[song_sheet['action']=='include']
    song_sheet = song_sheet.set_index(['artist', 'song', 'service'])
    
    artists_w_exclusions = song_sheet.loc[song_sheet['action']=='exclude'].index.get_level_values('artist').drop_duplicates()
    artists_w_inclusions = song_sheet.loc[song_sheet['action']=='include'].index.get_level_values('artist').drop_duplicates()
    artists_to_edit = set(artists_w_inclusions)|set(artists_w_exclusions)
    all_artists = kpis.index.levels[0]
    artists_to_keep = all_artists.difference(artists_to_edit)
    
    check = song_sheet.join(kpis)
    check = check.loc[check['streams'].isna()]
    if check.shape[0]:
        for record in check.reset_index().to_dict(orient='records'):
            warnings.warn(
                "Supposed to {action} {song} by {artist} for {service} "
                "but selection is not present.".format(**record)
            )
            
    out = kpis.join(song_sheet)
    out.loc[artists_to_keep, 'action'] = 'include'
    out.loc[artists_w_inclusions, 'action'] = out.loc[artists_w_inclusions, 'action'].fillna('exclude')
    out.loc[artists_w_exclusions, 'action'] = out.loc[artists_w_exclusions, 'action'].fillna('include')
    out = out.loc[out['action']!='exclude'].drop(columns='action')
    out.index = pd.util.hash_pandas_object(out.index)
    out = out.join(clean).reset_index(drop=True).set_index(idx_names)
    out.to_csv(DATEDIR/'Audit {}.csv'.format(DATEDIR))
    out = out.groupby(['artist', 'kpi']).sum().unstack('kpi').droplevel(0, axis=1)
    out = out.rename(columns={'pw': 'PW','ytd': 'YTD'})[['PW', 'YTD', 'recordings-28day', 'recordings-7day']]
    out.to_csv(DATEDIR/f'Output {DATEDIR}.csv')
    if return_df:
        return out
    
if __name__ == '__main__':
    
    
    #date = input("Please enter name of folder with song sheets")
    SONG_SHEET_NAME = 'Song Sheet.csv'
    
    parser = argparse.ArgumentParser(description='Generate KPI Sheet')
    parser.add_argument('date_directory', metavar='D', type=str,
                        help='Name of Date Folder')
    parser.add_argument('-s', dest='song_sheet_name', type=str,
                        default=None, help='Enter name of song sheet if not Song Sheet.csv')
    args = parser.parse_args()
    datedir = Path(args.date_directory)
    song_sheet_name = args.song_sheet_name or SONG_SHEET_NAME
    exit(main(datedir=datedir, song_sheet_name=song_sheet_name))