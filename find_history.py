import os, json, datetime

history = os.path.join(os.environ['APPDATA'], 'Code', 'User', 'History')
found = []

for root, dirs, files in os.walk(history):
    for f in files:
        if f == 'entries.json':
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as fp:
                    data = json.load(fp)
                for entry in data.get('entries', []):
                    name = entry.get('resource', '').replace('\\', '/')
                    if 'ai_router.py' in name:
                        timestamp = entry.get('timestamp', 0)
                        found.append((timestamp, root, name))
            except:
                pass

found.sort(key=lambda x: x[0], reverse=True)
print(f'Found {len(found)} history entries for ai_router.py:')
for ts, folder, name in found[:20]:
    if ts > 1e10:
        dt = datetime.datetime.fromtimestamp(ts / 1000)
    else:
        dt = datetime.datetime.fromtimestamp(ts)
    fname = name.split('/')[-1]
    # List files in folder
    try:
        fs = os.listdir(folder)
        py_files = [x for x in fs if x.endswith('.py')]
    except:
        py_files = []
    print(f'  {dt.strftime("%Y-%m-%d %H:%M:%S")} | {fname} | folder: {os.path.basename(folder)} | .py files: {len(py_files)}')
    for pf in py_files:
        fpath = os.path.join(folder, pf)
        size = os.path.getsize(fpath)
        print(f'    -> {pf} ({size} bytes)')

if not found:
    print('No history found for ai_router.py')
