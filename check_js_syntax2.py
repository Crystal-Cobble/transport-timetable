import re
from pathlib import Path
path = Path('departure-board.html')
html = path.read_text(encoding='utf8')
print('length', len(html))
print('script count', html.count('<script'))
print('end count', html.count('</script>'))
start = html.find('<script')
print('start idx', start)
start = html.find('>', start) + 1
print('start tag end', start)
end = html.rfind('</script>')
print('end idx', end)
code = html[start:end]
print('code starts', code[:80].replace('\n','\\n'))
print('code ends', code[-80:].replace('\n','\\n'))
# If script tag not found, show error
if start == 0 or end == -1 or end <= start:
    raise SystemExit('script extraction failed')
# test string of first line
lines = code.splitlines()
print('first line', lines[0])
print('second line', lines[1])
compile(code, '<embedded-script>','exec')
print('compiled ok')
