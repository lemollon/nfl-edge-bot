import pandas as pd

def normalize_roster(df: pd.DataFrame) -> pd.DataFrame:
    cols = {c.lower(): c for c in df.columns}
    df = df.rename(columns={
        cols.get('player','Player'): 'Player',
        cols.get('pos','Pos'): 'Pos',
        cols.get('% rostered','% Rostered'): '% Rostered'
    })
    df['% Rostered'] = pd.to_numeric(df['% Rostered'], errors='coerce')
    return df[['Player','Pos','% Rostered']]

def market_delta_by_position(roster_a: pd.DataFrame, roster_b: pd.DataFrame) -> pd.DataFrame:
    agg_a = roster_a.groupby("Pos")["% Rostered"].mean().rename("A_mean")
    agg_b = roster_b.groupby("Pos")["% Rostered"].mean().rename("B_mean")
    out = pd.concat([agg_a, agg_b], axis=1)
    out["delta_B_minus_A"] = out["B_mean"] - out["A_mean"]
    return out.reset_index()

def delta_scalar(delta_df: pd.DataFrame, weights: dict | None = None) -> float:
    weights = weights or {"QB":1.5,"RB":1.2,"WR":1.2,"TE":1.0,"D/ST":0.8,"K":0.5,"FLEX":1.0,"BN":0.0}
    s = 0.0; wsum = 0.0
    for _, row in delta_df.iterrows():
        pos = row["Pos"]; w = weights.get(pos, 1.0)
        if pd.notnull(row["delta_B_minus_A"]):
            s += float(row["delta_B_minus_A"]) * w; wsum += w
    return (s / wsum) if wsum else 0.0
