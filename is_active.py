import logging
import pandas as pd
from build_global_schemas import build_global_schemas

# ---- logging setup ----
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

# ---- load Excel file ----
INPUT_EXCEL = "schemas-a.xlsx"
df = pd.read_excel(INPUT_EXCEL)

# ---- normalize 'event_is_active' column ----
# Convert everything to boolean: True, 'TRUE', 'true' => True; False, 'FALSE' => False; blanks stay as None
def to_bool(val):
    if pd.isna(val):
        return None  # keep blanks as None
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        val_lower = val.strip().lower()
        if val_lower == 'true':
            return True
        elif val_lower == 'false':
            return False
    return None  # anything else treated as blank

df['event_is_active'] = df['event_is_active'].apply(to_bool)

# ---- filter active events ----
active_df = df[df['event_is_active'] == True]
skipped_df = df[df['event_is_active'] != True]  # False or blank

# ---- DRY RUN ----
deployed = build_global_schemas(active_df)

print("\nDRY RUN RESULT (only active events):")
print(f"{len(deployed)} schemas would be deployed\n")

for schema in deployed:
    print(
        f"{schema['event_value']} | "
        f"{schema['source_server']} | "
        f"{schema['schema_id']}"
    )

# ---- log skipped events ----
if not skipped_df.empty:
    print("\nSKIPPED EVENTS:")
    for _, row in skipped_df.iterrows():
        if row['event_is_active'] is False:
            status = "FALSE"
        else:  # None / blank
            status = "BLANK"
        print(f"[SKIPPED - {status}] {row['event_value']}")
