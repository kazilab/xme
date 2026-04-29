from xme_phases import build_xme_list, write_table

records = build_xme_list(tier="core")
write_table(records, "xme_phase_core.csv")
print(f"Wrote {len(records)} genes to xme_phase_core.csv")
