import requests

r = requests.get('http://localhost:8000/stats')
stats = r.json()

print("\n" + "="*60)
print("[DATABASE STATISTICS]")
print("="*60)
print(f"Total signals: {stats['total_signals']}")
print(f"BUY signals: {stats['buy_signals']}")
print(f"SELL signals: {stats['sell_signals']}")
print(f"WATCH signals: {stats['watch_signals']}")
print(f"Total labels: {stats['total_labels']}")
print(f"Total experiments: {stats['total_experiments']}")
print("="*60 + "\n")


