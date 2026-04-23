# 1. STATUS
LOCKED  
V7  
MONETIZATION POLICY

# 2. PURPOSE
This document locks the commercial policy of the partner engagement engine.

The system allows monetization only inside a protected ranking pipeline.
Monetization is subordinate to trust.
Monetization is not allowed to override quality or eligibility.
Monetization exists only as a weak signal, not as a command.

# 3. CURRENT PROTECTED PIPELINE
Locked pipeline order:

selection  
→ scoring  
→ quality gates  
→ token boost  
→ monetization signal  
→ preview reorder  
→ render

Preview reorder is the only final ordering stage.
Monetization participates only as one weak additive signal before preview reorder.
Monetization has no authority before quality gates.

# 4. CORE TRUST BOUNDARY
Quality gates are above monetization.
Offers removed by quality gates must stay removed.
Monetization cannot revive, rescue, or reinsert blocked offers.
Monetization cannot bypass eligibility.
Monetization cannot bypass selection.

If trust and monetization conflict, trust wins.

# 5. WHAT MONETIZATION IS ALLOWED TO DO
- Attach a weak internal commercial signal.
- Influence final preview order slightly.
- Operate only on already valid offers.
- Remain bounded and reversible.
- Remain subordinate to priority, scoring, and quality control.

# 6. WHAT MONETIZATION IS FORBIDDEN TO DO
- Sell guaranteed first place.
- Bypass quality gates.
- Revive rejected offers.
- Change eligibility.
- Change selection logic.
- Directly sort offers outside preview stage.
- Mutate analytics.
- Mutate balances.
- Mutate token accounting.
- Create billing side effects.
- Create storage side effects.
- Write purchases.
- Write payment history.
- Override trust controls.
- Become the dominant ranking signal.

# 7. POLICY INVARIANTS
- Monetization is additive, not absolute.
- Monetization is weak, not dominant.
- Monetization is optional, not structural.
- Monetization is reversible, not deeply embedded.
- Monetization is downstream from quality control.
- Monetization cannot change offer existence, only slight preview influence.
- Preview reorder remains the sole final ordering point.

# 8. ALLOWED FUTURE EVOLUTION
- Clearer operator controls.
- Explicit monetization modes.
- Sponsor labeling in UI only if added honestly and separately.
- Reporting and debug visibility.
- Policy-aware admin controls.
- Stronger monitoring of monetization influence.

Any future feature is allowed only if it does not violate the trust boundary.

# 9. FORBIDDEN FUTURE EVOLUTION
- Paid priority override.
- Direct top-slot sale.
- Hidden sponsor takeover of ranking.
- Monetization before quality gates.
- Monetization before selection.
- Monetization changing scoring formulas without governance lock.
- Monetization coupled with secret penalties or hidden bypasses.
- Silent architecture drift toward auction behavior.
- Any commercial feature that weakens trust controls.

# 10. OPERATOR PRINCIPLE
The system may earn through influence, but not through deception.

Commercial signal is allowed only inside truth-preserving system boundaries.

# 11. ROLLBACK PRINCIPLE
Monetization must remain removable with shallow rollback.

- Monetization layer should remain detachable.
- Preview additive commercial term should remain removable.
- Rollback must not require redesign of core selection, scoring, or gates.

# 12. SUCCESS DEFINITION
- Trust remains primary.
- Monetization remains bounded.
- Quality remains non-negotiable.
- Ranking remains explainable.
- Rollback remains simple.
- User-facing integrity remains intact.

# 13. FAILURE DEFINITION
- Money can override trust.
- Bad offers can buy visibility.
- Quality gates can be bypassed.
- Ranking becomes commercially opaque.
- Monetization becomes dominant.
- System drifts into pay-to-top behavior.
- Rollback becomes difficult.
- Business logic silently mutates architecture.

# 14. LOCK CONCLUSION
MONETIZATION is permitted inside AliMind only as a controlled, weak, reversible signal inside a trust-first pipeline.
Any attempt to move monetization above trust is a system violation.
