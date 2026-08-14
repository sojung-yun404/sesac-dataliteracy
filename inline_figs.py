"""report.html 의 src="FIG:xxx.png" 를 base64 data URI 로 치환한다.
   아티팩트는 외부 리소스를 못 불러오므로 이미지를 파일 안에 심어야 함."""
import base64
import pathlib
import re
import sys

from PIL import Image

SRC = pathlib.Path(sys.argv[1])          # 템플릿 (FIG: 플레이스홀더 포함)
OUT = pathlib.Path(sys.argv[2])          # 출력
WIDTH = {'FIG': 1600, 'FIGS': 1100}       # 본문 / 부록(작게)


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
OUT.write_text(html)
print(f'\n출력: {OUT}  ({len(html.encode())/1024/1024:.2f} MB)')
