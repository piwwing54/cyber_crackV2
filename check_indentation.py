import json
import os
from pathlib import Path

# Read the file
with open('frontend/telegram_bot.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Look around line 235
start = max(0, 234)  # 0-indexed
end = min(len(lines), 236)

print("Lines around 235:")
for i in range(start, end):
    prefix = '>>> ' if i == 234 else '    '
    print(f'{prefix}{i+1:3d}: {repr(lines[i][:60])}')
