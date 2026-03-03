What Phase 7 Does

The migration replaces the wide CSV format (year as row, months as columns, BE years) with standard long-format CSVs (date,price, CE dates). The payoff is in data_utils.py: the 12-line melt/BE-conversion block shrinks to one pd.read_csv call.

---
Concrete File Changes

3 sub-phases, commit after each:

---
Phase 7a — Migration script + generate CSVs (small)

Create src/data preparation/migrate_to_long_format.py:
- Reads all 4 crops from data/fix_year/{crop}/price_avg.csv (already CE years: 2004–2024)
- Melts wide → long, creates date column as YYYY-MM-DD
- Writes data/long_format/{crop}/price_avg.csv

Run it once to generate the CSVs. Each output is 252 rows (21 years × 12 months), two columns: date, price.

Verify: first row 2004-01-01,0.99, last row 2024-12-01,2.32 (cassava).

---
Phase 7b — Update path registry + simplify data_utils.py (small)

data_path.py — add 5 lines:
long_format_path = project_root / "data" / "long_format"
cassava_long  = long_format_path / "cassava"  / "price_avg.csv"
corn_long     = long_format_path / "corn"     / "price_avg.csv"
green_bean_long = long_format_path / "green_bean" / "price_avg.csv"
soybean_long  = long_format_path / "soybean"  / "price_avg.csv"

data_utils.py — replace the 12-line melt/BE block with 1 line:
# BEFORE (12 lines)
wide = pd.read_csv(data_file)
long = wide.melt(id_vars="year", ...).sort_values(...)
long["date"] = pd.to_datetime((long["year"] - 543)...)
long = long.set_index("date").sort_index()

# AFTER (1 line)
long = pd.read_csv(data_file, index_col="date", parse_dates=True)[["price"]]

The return signature and everything downstream stays identical.

---
Phase 7c — Update callers (small)

3 train scripts (__main__ blocks) — swap cassava_price_avg → cassava_long etc. (1 import line + dict values per file)

3 notebooks — update Cell 2: cassava_price_avg → cassava_long

---
Effort Assessment

┌─────────────────────────────┬───────────┬───────────────┬──────────────────────────────────────────┐
│          Sub-phase          │ New lines │ Changed lines │            Tool calls (est.)             │
├─────────────────────────────┼───────────┼───────────────┼──────────────────────────────────────────┤
│ 7a: migration script + run  │ ~40 new   │ 0             │ 2 (Write + Bash)                         │
├─────────────────────────────┼───────────┼───────────────┼──────────────────────────────────────────┤
│ 7b: data_path + data_utils  │ ~5 new    │ ~10 edited    │ 2 (Edit × 2)                             │
├─────────────────────────────┼───────────┼───────────────┼──────────────────────────────────────────┤
│ 7c: 3 scripts + 3 notebooks │ 0 new     │ ~18 edited    │ 4 (Edit × 3 + Bash script for notebooks) │
├─────────────────────────────┼───────────┼───────────────┼──────────────────────────────────────────┤
│ Total                       │ ~45       │ ~28           │ ~8                                       │
└─────────────────────────────┴───────────┴───────────────┴──────────────────────────────────────────┘

Verdict: LOW effort. Phase 7 is the simplest phase remaining. The migration script does the heavy lifting once; everything else is swapping path references.

---