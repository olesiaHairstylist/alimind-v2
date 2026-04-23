# 1. STATUS
LOCKED  
V12  
CONTROL PANEL SPEC

# 2. PURPOSE
The control panel exists to inspect the engagement engine, not to steer it silently.
The control panel is subordinate to runtime truth.
The control panel is subordinate to monetization policy.
The control panel is subordinate to audit policy.
The control panel exists for visibility, diagnosis, and comparison.
The control panel is not a ranking override interface.

# 3. CURRENT PROTECTED PIPELINE CONTEXT
Locked pipeline order:

selection  
→ scoring  
→ quality gates  
→ token boost  
→ monetization signal  
→ preview reorder  
→ explainability  
→ operator debug view  
→ audit trace  
→ render

Ranking is completed before panel visibility.
Panel visibility is downstream from runtime behavior.
Panel data must reflect runtime truth.
Panel actions must not rewrite ranking results.

# 4. CORE PANEL PRINCIPLE
The panel may reveal the system.
The panel may not secretly control the system.
The panel may compare runtime outputs.
The panel may not override runtime truth.
The panel may not become an invisible ranking authority.

The panel is for inspection, not intervention.

# 5. WHAT THE PANEL IS ALLOWED TO SHOW
- Final surviving offers.
- Compact operator debug snapshot.
- Explainability payload.
- Audit trace payload.
- Signal presence and signal values already attached to final offers.
- Stage flags and stage order.
- Monetization visibility where monetization exists.
- Token boost visibility where token boost exists.
- Quality gate pass status for surviving offers.
- Safe comparisons between final offers.
- Policy-aware summaries derived from existing runtime data.

# 6. WHAT THE PANEL IS FORBIDDEN TO SHOW AS CONTROL
- Direct rank editing.
- Drag-and-drop offer reordering.
- Force top placement.
- Manual bypass of quality gates.
- Manual reinsertion of removed offers.
- Hidden monetization override.
- Hidden token override.
- Hidden scoring override.
- Hidden priority override.
- Operator-only sponsor takeover.
- Silent mutation of final output.
- Silent runtime patching through panel controls.

# 7. WHAT THE PANEL IS ALLOWED TO DO
- Inspect.
- Compare.
- Filter visible audit and debug data for reading.
- View compact summaries.
- Expand internal details already present in runtime output.
- Display policy-related warnings.
- Display missing-layer warnings.
- Highlight suspicious combinations for operator awareness.
- Remain read-only with respect to ranking result.

# 8. WHAT THE PANEL IS FORBIDDEN TO DO
- Change ranking.
- Change scoring.
- Change eligibility.
- Change selection logic.
- Change quality gate behavior.
- Change token boost behavior.
- Change monetization behavior.
- Change explainability payloads.
- Change audit trace payloads.
- Change operator debug payloads.
- Mutate analytics.
- Mutate balances.
- Mutate token accounting.
- Mutate storage.
- Mutate callback formats.
- Mutate runtime truth.
- Hide commercial influence.
- Hide token influence.
- Hide missing layers.
- Hide inconsistent state.
- Act as a control channel without governance lock.

# 9. REQUIRED PANEL HONESTY
The panel must show runtime-attached signals honestly.
The panel must not rewrite or beautify runtime state.
The panel must not hide monetization when monetization is present.
The panel must not hide token boost when token boost is present.
The panel must not present audit as authority above runtime truth.
The panel must show missing internal layers as missing, not as passed.

The panel may organize truth, but it may not edit truth.

# 10. PANEL DATA SOURCES
The future panel may read only from already existing internal layers:
- Final offer state.
- `_explainability`.
- `_operator_debug`.
- `_audit_trace`.

The panel must remain downstream from these layers.
The panel must not invent new hidden ranking state without governance lock.
The panel must not become a parallel truth system.

# 11. OPERATOR BOUNDARY
Operator may inspect.
Operator may compare.
Operator may diagnose.
Operator may detect anomalies.
Operator may not steer ranking from the panel.
Operator may not override policy through the panel.
Operator may not treat the panel as an admin ranking console.

The operator may see the machine, but may not secretly steer the machine.

# 12. PANEL MODES (SPEC-LEVEL ONLY)
- Summary mode.
- Compare mode.
- Explainability mode.
- Audit trace mode.
- Policy warning mode.

These modes are visibility modes only.
These modes do not imply runtime authority.
These modes do not imply ranking edits.

# 13. ALLOWED FUTURE EVOLUTION
- Richer read-only views.
- Safer comparison tools.
- Stronger anomaly highlighting.
- Policy violation indicators.
- Operator health summaries.
- Controlled export specifications if separately governed.
- Clearer separation between inspect, compare, and warn modes.

Any future panel feature is allowed only if it preserves runtime truth and remains read-only with respect to ranking and control layers.

# 14. FORBIDDEN FUTURE EVOLUTION
- Manual ranking controls.
- Direct slot selling through the panel.
- Sponsor override controls.
- Hidden commercial amplification controls.
- Quality gate bypass controls.
- Token override controls.
- Silent operator-only runtime mutation.
- Panel-based scoring edits.
- Panel-based output rewriting.
- Panel becoming a hidden admin ranking console.
- Panel becoming a second truth system.
- Panel becoming a covert monetization tool.

# 15. ROLLBACK PRINCIPLE
Panel integration must remain removable with shallow rollback.

- Panel must remain downstream.
- Panel must remain detachable.
- Panel removal must not change ranking result.
- Panel removal must not require redesign of ranking, scoring, gates, or rendering.

# 16. SUCCESS DEFINITION
- Runtime truth remains primary.
- Panel remains read-only for ranking.
- Operator inspection remains possible.
- Policy visibility remains intact.
- Monetization visibility remains intact.
- Token visibility remains intact.
- Audit visibility remains intact.
- Rollback remains simple.
- User-facing integrity remains intact.

# 17. FAILURE DEFINITION
- Panel can change ranking directly.
- Panel can hide meaningful signals.
- Panel can hide commercial influence.
- Panel can bypass policy.
- Panel becomes a hidden control channel.
- Panel becomes an admin override path.
- Panel rewrites runtime truth.
- Panel creates silent architecture drift toward operator steering.
- Rollback becomes difficult.

# 18. LOCK CONCLUSION
The CONTROL PANEL is permitted inside AliMind only as a read-only, truth-preserving, downstream inspection surface.
Any attempt to turn the panel into hidden ranking control, policy bypass, or runtime override is a system violation.
