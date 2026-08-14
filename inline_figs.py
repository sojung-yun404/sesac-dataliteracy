"""report.html 의 src="FIG:xxx.png" 를 base64 data URI 로 치환한다.
   아티팩트는 외부 리소스를 못 불러오므로 이미지를 파일 안에 심어야 함."""
import base64
import pathlib
import re
import sys

from PIL import Image

SRC = pathlib.Path(sys.argv[1])          # 템플릿 (FIG: 플레이스홀더 포함)
OUT = pathlib.Path(sys.argv[2])          # 출력
STANDALONE = '--standalone' in sys.argv  # 브라우저에서 바로 열리는 완전한 문서로
WIDTH = {'FIG': 1600, 'FIGS': 1100}       # 본문 / 부록(작게)

HEAD = '''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="2023년 1~3월 저지시티 Citi Bike 13,696건 탐색적 데이터 분석">
<style>*,*::before,*::after{box-sizing:border-box}
body{margin:0}img{max-width:100%}</style>
'''
FOOT = '\n</body>\n</html>\n'


def encode(name, tag='FIG'):
    p = pathlib.Path(name)
    im = Image.open(p)
    mw = WIDTH[tag]
    if im.width > mw:                    # 웹 표시용으로만 쓰므로 축소
        h = round(im.height * mw / im.width)
        im = im.resize((mw, h), Image.LANCZOS)
    tmp = pathlib.Path('.fig_tmp.png')
    im.convert('RGB').save(tmp, 'PNG', optimize=True)
    b = tmp.read_bytes()
    tmp.unlink()
    print(f'  {name:28s} {p.stat().st_size/1024:6.0f}KB -> {len(b)/1024:6.0f}KB'
          f'  ({im.width}x{im.height})')
    return 'data:image/png;base64,' + base64.b64encode(b).decode()


html = SRC.read_text()
print('이미지 인라인:')
html = re.sub(r'(FIGS?):([\w.]+\.png)',
              lambda m: encode(m.group(2), m.group(1)), html)

if STANDALONE:
    # 아티팩트는 <head>/<body>를 알아서 감싸주지만, 깃허브 페이지는 아니다.
    # <style> 블록이 끝나는 지점에서 head/body 를 가른다.
    cut = html.index('</style>') + len('</style>')
    html = HEAD + html[:cut] + '\n</head>\n<body>' + html[cut:] + FOOT

OUT.write_text(html)
print(f'\n출력: {OUT}  ({len(html.encode())/1024/1024:.2f} MB)')
