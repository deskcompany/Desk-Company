import sys
orig, trecho, saida = sys.argv[1:4]
html = open(orig, encoding='utf-8').read()
extra = open(trecho, encoding='utf-8').read()
assert html.count('</body>') == 1
open(saida, 'w', encoding='utf-8').write(html.replace('</body>', extra + '\n</body>'))
print('ok')
