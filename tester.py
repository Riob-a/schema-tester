import pandas as pd

# Load your CSV or TSV file
df = pd.read_excel("schemas-a.xlsx")  # or use sep="\t" if tab-separated

# Check rows where 'event_is_active' is missing or empty
missing_active = df[df['event_is_active'].isna() | (df['event_is_active'].astype(str).str.strip() == '')]

# Print the rows or just the event_values
print(missing_active[['event_value', 'event_is_active']])
