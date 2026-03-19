# -----------------------------
# CLEAN IDs FIRST (ONLY ONCE)
# -----------------------------
def clean(x):
    return str(x).strip().replace(".0", "")

update["LegacyId"] = update["LegacyId"].apply(clean)
crm["Recurring Gift Transaction Id"] = crm["Recurring Gift Transaction Id"].apply(clean)

# -----------------------------
# CREATE A CLEAN MAPPING TABLE
# -----------------------------
crm_map = crm[[
    "Recurring Gift Transaction Id",
    "Recurring Gift Id"
]].drop_duplicates()

# -----------------------------
# PERFORM MERGE (DO NOT TOUCH AFTER)
# -----------------------------
update = update.merge(
    crm_map,
    how="left",
    left_on="LegacyId",
    right_on="Recurring Gift Transaction Id"
)

# -----------------------------
# FINAL FIELD ASSIGNMENT
# -----------------------------
update["RecurringId"] = update["Recurring Gift Id"]
update["NewTransactionId"] = "rd2-" + update["LegacyId"]
update["TransactionSource"] = "RaiseDonors"
