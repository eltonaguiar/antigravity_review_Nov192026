#!/usr/bin/env python3
"""Review of "meme coin endorsements" from the CoinGecko top-100 table (2026-11-24).

WHAT "ENDORSEMENT" CAN MEAN HERE
  Sell-side analyst coverage: ZERO. Measured earlier - Finnhub /stock/recommendation returns
  0 records for DOGE/SHIB/PEPE/BONK/WIF/FLOKI while AAPL/COIN/MSTR return 4. Crypto research
  (Messari/Kaiko/CoinMetrics) exists but publishes no per-token buy/hold consensus with a
  target. So there is no endorsement channel in the sell-side sense.

  What the table offers instead is three fields: market-cap RANK (a survivorship/popularity
  measure), 24h VOLUME (an executability measure), and price change (momentum). Only volume is
  decision-relevant for a position-sizing question, because it bounds the size you can leave.

THIS SCRIPT
  Treats the pasted table as the dataset. Computes concentration, breadth, volume/mcap
  turnover, and - the decisive one - the maximum position a retail account can take at 1% of
  daily volume before it IS the market.

DATA: transcribed from the CoinGecko top-100 meme table, 2026-11-24. mcap in $M, vol in $K.
"""
from __future__ import annotations

import json
import pathlib
import statistics
import sys

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out" / "meme_endorsement_review.json"

# (rank, ticker, mcap_$M, vol_$K, chg24_pct, chg7d_pct)
T = [
 (1,"DOGE",8640,511270,-3.49,-5.70),(2,"SHIB",2100,43460,-3.78,-6.32),
 (3,"PEPE",1420,338650,-3.14,-8.87),(4,"APEPE",293.18,16950,0.72,12.10),
 (5,"PENGU",265.47,62130,-6.46,-6.55),(6,"SPX",252.24,4900,-5.70,-12.64),
 (7,"BONK",187.28,23430,-3.18,-8.97),(8,"FLOKI",156.09,9010,-3.57,-8.87),
 (9,"DOGE(peg)",140.78,470.71,-3.16,-5.37),(10,"WIF",120.52,28840,-5.29,-9.05),
 (11,"NPC",83.07,3200,-10.62,-11.75),(12,"FARTCOIN",78.70,9590,-6.04,-11.08),
 (13,"DOG",65.50,382.01,-3.73,-7.72),(14,"CHEEMS",56.55,319.73,-3.27,-5.25),
 (15,"ORDI",54.23,8700,-4.81,-5.86),(16,"BANANAS31",46.79,3080,-3.39,-8.47),
 (17,"BABYDOGE",44.93,1280,-3.81,-4.54),(18,"BAN",40.46,2730,-4.76,4.37),
 (19,"PURR",39.61,900.25,-9.88,-25.80),(20,"TURBO",38.21,5270,-3.48,-8.26),
 (21,"TOSHI",32.67,2140,-4.87,-2.66),(22,"SHIB(peg)",32.67,11.74,-3.52,-6.32),
 (23,"REKT",32.27,1000,-3.66,16.17),(24,"LOBO",31.51,9.55,0.35,-11.87),
 (25,"BOME",31.03,5010,-4.82,-8.77),(26,"MOG",30.78,6310,-3.41,2.49),
 (27,"SNEK",30.60,820.31,-8.59,-7.09),(28,"BRETT",30.02,2270,-4.43,-9.82),
 (29,"NOT",28.66,2850,-3.08,-5.78),(30,"GEKKO",28.31,0.60937,-4.01,-26.97),
 (31,"PNUT",25.79,8010,-4.13,-10.69),(32,"MEW",25.16,1800,-4.29,-5.98),
 (33,"POPCAT",24.41,5070,-6.80,-11.37),(34,"DEGEN",24.40,2250,-3.75,-1.20),
 (35,"PEOPLE",24.28,5310,-2.66,-5.56),(36,"MOODENG",24.26,5190,-6.61,-8.63),
 (37,"HUNDRED",21.95,1.86,0.02,1.38),(38,"UTYA",21.72,351.87,-7.78,-26.71),
 (39,"WKC",20.61,90.05,-6.76,-22.29),(40,"ZEREBRO",20.39,5000,-5.86,-3.36),
 (41,"NEIRO",19.54,3020,-3.25,-5.20),(42,"PIPPIN",19.07,3560,4.25,74.21),
 (43,"MEME",18.51,4350,-3.49,-9.76),(44,"BURN",15.61,24.68,-0.78,-13.01),
 (45,"ELON",15.34,2300,-8.43,-20.48),(46,"FRTC",14.83,43.98,-0.03,-0.01),
 (47,"GIGA",13.08,1570,-7.01,-14.27),(48,"DOGS",12.48,1950,-5.11,-8.90),
 (49,"$CWIF",12.03,0.60316,3.02,15.64),(50,"AIXBT",11.64,1970,-3.31,-9.64),
 (51,"HAROLD",11.26,1.26,-6.17,-12.27),(52,"AIC",10.76,68.32,-5.12,-5.50),
 (53,"OSAK",10.24,59.73,-7.33,-3.97),(54,"GOAT",10.17,1190,-4.09,-5.25),
 (55,"CAT",9.64,617.58,-5.84,-11.03),(56,"GRIFFAIN",9.56,2640,-2.88,-1.14),
 (57,"BONE",9.54,2390,-2.18,-3.37),(58,"BALD",9.21,0.00236,-3.02,-7.78),
 (59,"BITCOIN",8.93,323.96,-7.25,-14.93),(60,"ACT",8.18,4340,-1.15,-1.41),
 (61,"ANDY",8.12,79.75,-7.96,-4.37),(62,"NST",7.97,145.53,-5.75,-14.04),
 (63,"BINK",7.85,0.00897,-5.38,-5.83),(64,"BERT",7.61,607.50,-7.71,-22.55),
 (65,"AVA",7.59,2700,0.98,27.92),(66,"BARA",7.50,14.04,-0.61,3.93),
 (67,"KOMA",7.49,962.13,-4.46,-1.77),(68,"CORGIAI",7.40,3.93,-1.59,-4.55),
 (69,"PONKE",7.35,2260,-2.10,-6.34),(70,"CHILLGUY",6.80,3670,-2.96,-7.67),
 (71,"PEPECOIN",6.37,129.61,-14.88,-18.79),(72,"PEP",6.20,90.95,-4.13,-0.36),
 (73,"LOFI",6.09,204.87,-5.99,-11.45),(74,"SMOLE",6.00,0.05152,-6.35,-4.85),
 (75,"COQ",5.99,2210,-1.88,10.96),(76,"AHT",5.97,63.31,-1.80,-2.21),
 (77,"PUPPIES",5.84,465.77,-3.73,13.50),(78,"WOLF",5.72,293.97,-7.59,-6.64),
 (79,"ROSA",5.71,209.41,-8.04,-15.41),(80,"CROB",5.35,0.02016,-1.20,-7.38),
 (81,"BNBTIGEROG",5.30,10.05,0.00,0.00),(82,"PEPPER",5.21,9.45,-3.28,10.46),
 (83,"PTGC",5.05,4.50,-1.62,-3.97),(84,"CULT",4.89,92.07,-4.15,-18.42),
 (85,"PNDC",4.87,14.50,-15.19,-18.80),(86,"MONA",4.85,3.92,-2.93,-5.47),
 (87,"BABYSHIBAINU",4.84,0.08865,-1.86,-6.37),(88,"PIKA",4.78,3.53,-1.99,-2.76),
 (89,"PEPECAT",4.64,17.03,0.29,-2.21),(90,"DOG(OTD)",4.57,11.02,-4.08,-3.49),
 (91,"PIT",4.35,56.86,-3.23,-5.24),(92,"HTM",4.32,8.25,-4.62,-10.33),
 (93,"SQGROW",4.24,2.47,-7.93,6.20),(94,"VDOGE",4.16,0.0,-4.96,-6.05),
 (95,"UFD",4.13,31.47,-5.17,-9.58),(96,"AURA",4.10,209.39,-7.66,-17.87),
 (97,"KEKIUS",4.00,2230,3.65,1.13),(98,"PORK",3.95,10.03,-4.45,-15.16),
 (99,"HOSKY",3.89,3.32,-4.07,4.99),(100,"LADYS",3.75,97.78,-3.93,-4.11),
]


def main() -> int:
    rows = [{"rank": r, "ticker": t, "mcap_musd": m, "vol_musd": v / 1000.0,
             "chg24": c24, "chg7d": c7} for r, t, m, v, c24, c7 in T]
    total_mcap = sum(r["mcap_musd"] for r in rows)
    total_vol = sum(r["vol_musd"] for r in rows)

    print("=" * 78)
    print("1. CONCENTRATION — is 'the meme sector' a sector or three coins?")
    print("=" * 78)
    top3 = sum(r["mcap_musd"] for r in rows[:3])
    top10 = sum(r["mcap_musd"] for r in rows[:10])
    print(f"   top-100 listed mcap: ${total_mcap/1000:.2f}B   daily volume: ${total_vol/1000:.2f}B")
    print(f"   top 3  = {100*top3/total_mcap:5.1f}% of listed cap")
    print(f"   top 10 = {100*top10/total_mcap:5.1f}% of listed cap")
    print("   => a '5-20% satellite allocation to meme coins' is ~80% a bet on DOGE+SHIB+PEPE.")

    print("\n" + "=" * 78)
    print("2. BREADTH — did the sector actually endorse itself today?")
    print("=" * 78)
    d24 = [r for r in rows if r["chg24"] < 0]
    d7 = [r for r in rows if r["chg7d"] < 0]
    med7 = statistics.median([r["chg7d"] for r in rows])
    print(f"   negative on 24h: {len(d24)}/100      negative on 7d: {len(d7)}/100")
    print(f"   median 7d change: {med7:+.2f}%")
    pos7 = sorted([r for r in rows if r["chg7d"] > 0], key=lambda r: -r["chg7d"])
    print(f"   positive on 7d : {len(pos7)}/100 -> " +
          ", ".join(f"{r['ticker']} {r['chg7d']:+.1f}%" for r in pos7[:8]))
    print("   => the sector moves as one trade; the handful of winners are the exception,")
    print("      and a 7-day window is far too short to distinguish skill from beta.")

    print("\n" + "=" * 78)
    print("3. TURNOVER (volume/mcap) — the only field that bounds executability")
    print("=" * 78)
    for r in rows:
        r["turnover_pct"] = 100.0 * r["vol_musd"] / r["mcap_musd"] if r["mcap_musd"] else 0.0
    buckets = [("<0.10%", 0.10), ("0.10-1%", 1.0), ("1-5%", 5.0), ("5-20%", 20.0), (">20%", 1e9)]
    prev = -1.0
    for label, hi in buckets:
        n = sum(1 for r in rows if prev < r["turnover_pct"] <= hi)
        print(f"   turnover {label:<10} {n:>3} coins")
        prev = hi
    dead = [r for r in rows if r["turnover_pct"] < 0.10]
    print(f"\n   {len(dead)} of 100 trade under 0.10% of cap PER DAY. These are not")
    print("   instruments you can enter and exit; they are instruments you can only enter.")

    print("\n" + "=" * 78)
    print("4. MAX POSITION AT 1% OF DAILY VOLUME — the retail-size test")
    print("=" * 78)
    print("   A position larger than 1% of daily volume moves the market against you and")
    print("   cannot be exited at the quoted price. That fixes the largest sane size:")
    for cap_usd in (1000, 10000, 50000):
        ok = [r for r in rows if 0.01 * r["vol_musd"] * 1e6 >= cap_usd]
        print(f"   ${cap_usd:>6,} position is executable in {len(ok):>2}/100 coins")
    worst = sorted(rows, key=lambda r: r["vol_musd"])[:6]
    print("\n   least executable in the top 100:")
    for r in worst:
        print(f"     #{r['rank']:<4}{r['ticker']:<12} mcap ${r['mcap_musd']:>7.2f}M  "
              f"daily vol ${r['vol_musd']*1000:>10,.0f}  max 1% pos ${0.01*r['vol_musd']*1e6:>8,.0f}")
    print("\n   => at 1% participation, a $10,000 position is genuinely executable in only a")
    print("      minority of the top 100. For the rest the 20-52bp cost band is not the")
    print("      binding constraint - the absence of a counterparty is.")

    print("\n" + "=" * 78)
    print("5. TICKER COLLISIONS — why the earlier 'zero coverage' probe cannot be trusted")
    print("=" * 78)
    seen: dict[str, list] = {}
    for r in rows:
        base = r["ticker"].replace("(peg)", "").replace("(OTD)", "")
        seen.setdefault(base, []).append(r)
    for base, grp in seen.items():
        if len(grp) > 1:
            print(f"   {base}: " + ", ".join(f"#{g['rank']} ${g['mcap_musd']:.1f}M" for g in grp))
    print("   plus PEPE/PEPECOIN/PEP and BITCOIN(HPOS10I) as distinct assets sharing a stem.")
    print("   A zero from an equity-recommendation endpoint on a bare ticker string cannot")
    print("   distinguish 'not an equity' from 'no coverage' - now demonstrated on real rows.")

    print("\n" + "=" * 78)
    print("6. VERDICT ON 'ENDORSEMENT'")
    print("=" * 78)
    print("   There is no sell-side endorsement to review. What the table provides is")
    print("   survivorship (cap rank), correlation (breadth) and liquidity (volume).")
    print(f"   By the only decision-relevant field - volume - {len(dead)}/100 are unexitable and")
    print(f"   a $10k position clears 1% of daily volume in {sum(1 for r in rows if 0.01*r['vol_musd']*1e6>=10000)}/100.")
    print("   Cap rank is not an endorsement; it is the residue of past speculation.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "total_mcap_musd": total_mcap, "total_vol_musd": total_vol,
        "top3_share_pct": 100 * top3 / total_mcap,
        "top10_share_pct": 100 * top10 / total_mcap,
        "negative_24h": len(d24), "negative_7d": len(d7), "median_7d_pct": med7,
        "turnover_under_0_1pct_count": len(dead),
        "executable_10k_count": sum(1 for r in rows if 0.01 * r["vol_musd"] * 1e6 >= 10000),
        "rows": rows}, indent=2))
    print(f"\n   written: {OUT.relative_to(HERE)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
