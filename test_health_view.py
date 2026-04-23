from app.modules import read_health_snapshot
from app.modules import render_health_snapshot

snapshot = read_health_snapshot()
text = render_health_snapshot(snapshot)

print()
print(text)
print()