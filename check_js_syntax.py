html = open('departure-board.html', 'r', encoding='utf8').read()
start = html.find('<script')
if start == -1:
    raise SystemExit('script start not found')
start = html.find('>', start) + 1
end = html.rfind('</script>')
if end == -1:
    raise SystemExit('script end not found')
code = html[start:end]
compile(code, 'departure-board.html', 'exec')
print('JS syntax OK')
