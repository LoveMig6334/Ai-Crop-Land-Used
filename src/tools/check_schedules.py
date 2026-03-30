"""Quick script to compare greedy and brute-force optimal schedules."""
import sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent.parent))

import numpy as np
from datetime import datetime, timedelta
from src.util.data_path import LSTM_3L_for
from src.util.output_io import load_forecast_csv

crops_map = {"Cassava": "cassava", "Corn": "corn", "Green Bean": "green_bean", "Soybean": "soybean"}
time_grow = {"Cassava": 250, "Corn": 120, "Green Bean": 80, "Soybean": 90}
crops_yield_per_rai = {"Cassava": 3500, "Corn": 1500, "Green Bean": 245, "Soybean": 300}

crop_data = {}
crop_price_avg = {}
for cn, ck in crops_map.items():
    df = load_forecast_csv(LSTM_3L_for, ck)
    crop_data[cn] = {"dates": df.index.tolist(), "prices": df["forecast_price"].tolist()}
    crop_price_avg[cn] = np.mean(df["forecast_price"].tolist())

for cn, d in crop_data.items():
    d["norm_prices"] = [p / crop_price_avg[cn] for p in d["prices"]]

harvest_incomes = {}
for cn, d in crop_data.items():
    norm = d["norm_prices"]
    dates = d["dates"]
    peak_idx = int(np.argmax(norm))
    peak_date = dates[peak_idx]
    peak_norm = norm[peak_idx]
    actual_price = peak_norm * crop_price_avg[cn]
    income = crops_yield_per_rai[cn] * actual_price
    harvest_incomes[cn] = {"harvest_date": peak_date, "peak_price": peak_norm, "income": income}

crop_candidates = []
for cn, d in harvest_incomes.items():
    crop_candidates.append({"crop": cn, "income": d["income"], "duration": time_grow[cn],
                           "harvest_date": d["harvest_date"], "peak_price": d["peak_price"]})

year_start = datetime(2024, 1, 1)
year_end = datetime(2024, 12, 31)

def find_price_at_date(crop, date):
    d = crop_data[crop]
    dates, norms = d["dates"], d["norm_prices"]
    for i in range(len(dates) - 1):
        if dates[i] <= date <= dates[i + 1]:
            frac = (date - dates[i]).total_seconds() / (dates[i + 1] - dates[i]).total_seconds()
            return norms[i] + frac * (norms[i + 1] - norms[i])
    if date <= dates[0]: return norms[0]
    if date >= dates[-1]: return norms[-1]
    return None

def calc_income(crop, harvest_date, norm_price=None):
    if norm_price is None:
        norm_price = find_price_at_date(crop, harvest_date)
        if norm_price is None: return 0.0
    return crops_yield_per_rai[crop] * norm_price * crop_price_avg[crop]

def schedule(candidates):
    sched = []
    used = set()
    intervals = []
    for cand in candidates:
        crop = cand["crop"]
        if crop in used: continue
        h = cand["harvest_date"]
        dur = cand["duration"]
        p = h - timedelta(days=dur)
        conflict = any(not (p >= e or h <= s) for s, e in intervals)
        if not conflict:
            intervals.append((p, h))
            sched.append({"crop": crop, "start": p, "end": h, "income": cand["income"], "strategy": "original"})
            used.add(crop); continue
        gaps = []
        if intervals:
            intervals.sort(key=lambda x: x[0])
            if intervals[0][0] > year_start: gaps.append((year_start, intervals[0][0]))
            for i in range(len(intervals) - 1):
                if intervals[i + 1][0] - intervals[i][1] >= timedelta(days=dur):
                    gaps.append((intervals[i][1], intervals[i + 1][0]))
            if intervals[-1][1] < year_end: gaps.append((intervals[-1][1], year_end))
        else:
            gaps.append((year_start, year_end))
        placed = False
        for gs, ge in gaps:
            if ge - gs >= timedelta(days=dur):
                ec = min(ge, year_end)
                sc = ec - timedelta(days=dur)
                if sc >= gs:
                    np_ = find_price_at_date(crop, ec) or cand["peak_price"]
                    ni = calc_income(crop, ec, np_)
                    sched.append({"crop": crop, "start": sc, "end": ec, "income": ni, "strategy": "shifted"})
                    intervals.append((sc, ec)); used.add(crop); placed = True; break
        if placed: continue
        if gaps:
            lg = max(gaps, key=lambda x: x[1] - x[0])
            ec = min(lg[1], year_end)
            sc = ec - timedelta(days=dur)
            if year_start <= ec <= year_end:
                np_ = find_price_at_date(crop, ec) or cand["peak_price"]
                ni = calc_income(crop, ec, np_)
                sched.append({"crop": crop, "start": sc, "end": ec, "income": ni, "strategy": "prev_year"})
                intervals.append((sc, ec)); used.add(crop); continue
    return sched

# Brute-force optimal
from itertools import permutations
best_income, best_sched, best_perm = 0, None, None
for perm in permutations(crop_candidates):
    s = schedule(list(perm))
    t = sum(x["income"] for x in s)
    if t > best_income:
        best_income, best_sched, best_perm = t, s, [c["crop"] for c in perm]

# Greedy
crop_candidates.sort(key=lambda x: x["income"], reverse=True)
greedy_sched = schedule(crop_candidates)
greedy_total = sum(x["income"] for x in greedy_sched)

print("=== BRUTE-FORCE OPTIMAL ===")
print(f"Order: {best_perm}")
print(f"Total: {best_income:,.0f} THB")
for s in best_sched:
    print(f"  {s['crop']:12s} {s['start'].strftime('%Y-%m-%d')} -> {s['end'].strftime('%Y-%m-%d')}  {s['strategy']:10s}  {s['income']:>10,.0f}")

print(f"\n=== GREEDY ===")
print(f"Order: {[c['crop'] for c in crop_candidates]}")
print(f"Total: {greedy_total:,.0f} THB")
scheduled_names = set()
for s in greedy_sched:
    scheduled_names.add(s["crop"])
    print(f"  {s['crop']:12s} {s['start'].strftime('%Y-%m-%d')} -> {s['end'].strftime('%Y-%m-%d')}  {s['strategy']:10s}  {s['income']:>10,.0f}")
excluded = set(cn for cn in crops_map) - scheduled_names
if excluded:
    print(f"  EXCLUDED: {excluded}")

print(f"\nGap: {best_income - greedy_total:,.0f} THB ({(best_income - greedy_total)/best_income*100:.1f}%)")

# Monoculture comparison
print("\n=== MONOCULTURE ===")
best_mono_name, best_mono_inc = "", 0
for cn, d in harvest_incomes.items():
    print(f"  {cn}: {d['income']:,.0f}")
    if d["income"] > best_mono_inc:
        best_mono_name, best_mono_inc = cn, d["income"]
print(f"Best: {best_mono_name} ({best_mono_inc:,.0f})")
print(f"BF optimal / best mono = {best_income/best_mono_inc:.2f}x")
print(f"Greedy / best mono = {greedy_total/best_mono_inc:.2f}x")
