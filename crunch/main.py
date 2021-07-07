import re
import warnings
from pathlib import Path

import pandas as pd

SONG_SHEET_NAME = "song_sheet.csv"
OUTPUT_NAME = "output.csv"
AUDIT_NAME = "audit.csv"

__all__ = ["SONG_SHEET_NAME", "OUTPUT_NAME", "AUDIT_NAME", "main"]


def clean_string_col(col):
    try:
        out = col.str.strip().str.replace(" +", " ", regex=True).str.lower()
    except AttributeError:
        out = col

    return out


def main(date_dir, song_sheet_name, return_df=False):

    date_dir = Path(date_dir)

    if not date_dir.is_absolute():
        pass

    pat = re.compile(
        r"^(?P<artist>.*) (?P<kpi>recordings\-\d{1,2}day|PW|YTD)(?: \(\d+\))?\.csv$"
    )
    stat_sheets = []
    for service_dir in date_dir.iterdir():
        if not service_dir.is_dir():
            continue
        for stat_sheet in service_dir.iterdir():
            if stat_sheet.name == ".ipynb_checkpoints":
                continue
            # get KPI and artist from file
            match = re.match(pat, stat_sheet.name)
            if not match:
                continue
            stats_df = pd.read_csv(stat_sheet)
            stats_df.columns = stats_df.columns.str.lower()
            stats_df = (
                stats_df.rename(columns={"plays": "streams"})[
                    ["song", "streams"]
                ].assign(service=service_dir.name, **match.groupdict())
                # .apply(clean_string_col)
                .set_index(["artist", "song", "service", "kpi"])
            )
            stat_sheets.append(stats_df)
    kpis = pd.concat(stat_sheets)
    # songs w same names like singles and albums, etc
    idx_names = kpis.index.names
    kpis = kpis.groupby(idx_names).sum()
    clean = kpis.drop(columns="streams").reset_index()
    kpis = kpis.reset_index().apply(clean_string_col).set_index(kpis.index.names)
    clean.index = pd.util.hash_pandas_object(kpis.index)

    song_sheet = pd.read_csv(date_dir / song_sheet_name)
    song_sheet.columns = song_sheet.columns.str.strip().str.lower()
    song_sheet = song_sheet.dropna(how="all")
    song_sheet["artist"] = song_sheet["artist"].pad()
    song_sheet["song"] = song_sheet["include"].combine_first(song_sheet["exclude"])
    song_sheet = song_sheet.set_index(["artist", "song"])
    song_sheet["action"] = song_sheet[["include", "exclude"]].notna().idxmax(axis=1)
    song_sheet = song_sheet.reset_index()
    song_sheet = song_sheet.melt(
        id_vars=("artist", "song", "action"),
        value_vars=("spotify", "apple"),
        var_name="service",
        value_name="keep",
    )
    song_sheet = song_sheet.loc[song_sheet["keep"].notna()]
    song_sheet = song_sheet.drop(columns="keep")
    song_sheet = song_sheet.apply(clean_string_col)
    song_sheet = song_sheet.set_index(["artist", "song", "service"])

    art_w_exc = (
        song_sheet.loc[song_sheet["action"] == "exclude"]
        .index.get_level_values("artist")
        .drop_duplicates()
    )
    # artists with inclusios
    art_w_inc = (
        song_sheet.loc[song_sheet["action"] == "include"]
        .index.get_level_values("artist")
        .drop_duplicates()
    )
    art_to_edit = set(art_w_inc) | set(art_w_exc)
    all_art = kpis.index.levels[0]
    art_to_keep = all_art.difference(art_to_edit)

    check = song_sheet.join(kpis)
    check = check.loc[check["streams"].isna()]
    if check.shape[0]:
        for record in check.reset_index().to_dict(orient="records"):
            warnings.warn(
                "Supposed to {action} {song} by {artist} for {service} "
                "but selection is not present.".format(**record)
            )

    out = kpis.join(song_sheet)
    out.loc[art_to_keep, "action"] = "include"
    out.loc[art_w_inc, "action"] = out.loc[art_w_inc, "action"].fillna("exclude")
    out.loc[art_w_exc, "action"] = out.loc[art_w_exc, "action"].fillna("include")
    out = out.loc[out["action"] != "exclude"].drop(columns="action")
    out.index = pd.util.hash_pandas_object(out.index)
    out = out.join(clean).reset_index(drop=True).set_index(idx_names)
    out.to_csv(date_dir / f"{date_dir.name}_{AUDIT_NAME}")
    out = (
        out.groupby(["artist", "kpi"])
        .sum()
        .unstack("kpi")
        .droplevel(0, axis=1)
        .rename(columns={"pw": "PW", "ytd": "YTD"})[
            ["PW", "YTD", "recordings-28day", "recordings-7day"]
        ]
    )
    out.to_csv(date_dir / f"{date_dir.name}_{OUTPUT_NAME}")
    if return_df:
        return out
