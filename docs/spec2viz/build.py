"""Rebuild the spec2viz catalog and portable SVG views from semantic YAML."""
from pathlib import Path
import argparse
import base64
import html
import subprocess
import yaml

ROOT = Path(__file__).resolve().parent


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exports-only', action='store_true', help='Reuse existing Mermaid and HTML outputs')
    args = parser.parse_args()
    specs = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'specs').glob('*.yml'))
    if not args.exports_only:
        run('spec2viz', 'diagram', 'validate', *specs)
        run('spec2viz', 'diagram', 'render', *specs, '--backend', 'mermaid', '--out', 'out/mermaid')
        run('spec2viz', 'catalog', 'build', '--config', 'catalog.yml', '--out', 'index.html')

    export_views(ROOT)


def export_views(root):
    """Export a spec2viz catalog with pre-rendered Mermaid to portable views."""
    catalog = yaml.safe_load((root / 'catalog.yml').read_text())['diagram_store']
    items = catalog['items']
    title_text = catalog.get('title', 'pron')
    subtitle = catalog.get('brand_subtitle', 'Vistas derivadas del código fuente.')
    title_html = html.escape(title_text)
    subtitle_html = html.escape(subtitle)
    svg_dir = root / 'out/svg'
    svg_dir.mkdir(parents=True, exist_ok=True)
    markdown = [f'# {title_text}', '', subtitle, '']
    cards = []
    nav = []
    for item in items:
        ident = item['id']
        title = item['title']
        svg = f'out/svg/{Path(item["mmd"]).stem}.svg'
        subprocess.run(['mmdc', '-i', item['mmd'], '-o', svg, '-t', 'neutral', '-b', 'white', '-w', '1800', '-q'], cwd=root, check=True)
        notes = '\n'.join(f'- {note}' for note in item['notes'])
        mermaid = (root / item['mmd']).read_text()
        markdown.extend([f'## {title}', '', item['desc'], '', notes, '', f'```mermaid\n{mermaid}\n```', ''])
        esc = html.escape
        nav.append(f'<a href="#{ident}">{esc(item["nav"])}</a>')
        encoded_svg = base64.b64encode((root / svg).read_bytes()).decode('ascii')
        inline_svg = f'<img src="data:image/svg+xml;base64,{encoded_svg}" alt="{esc(title)}">'
        cards.append(f'<section id="{ident}"><h2>{esc(title)}</h2><p>{esc(item["desc"])}</p>'
                     f'<div class="diagram">{inline_svg}</div><ul>' +
                     ''.join(f'<li>{esc(note)}</li>' for note in item['notes']) +
                     f'</ul><p><a href="{svg}">Abrir SVG</a> · '
                     f'<a href="{item["specs"][0]}">YAML semántico</a></p></section>')
    (root / 'diagrams.md').write_text('\n'.join(markdown))
    page = '''<!doctype html><html lang="es"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CATALOG_TITLE</title>
<style>
*{box-sizing:border-box}body{margin:0;font:16px/1.6 system-ui,sans-serif;color:#182839;background:#eef2f6}
nav{position:fixed;inset:0 auto 0 0;width:270px;padding:24px;background:#142638;color:#fff;overflow:auto}
nav a{display:block;color:#dce8f5;text-decoration:none;padding:8px 0;font-size:14px}
main{margin-left:270px;padding:36px;max-width:1800px}h1{line-height:1.15;font-size:36px}
section{background:white;padding:28px;margin:24px 0;border:1px solid #d9e1e8;border-radius:12px;scroll-margin-top:20px}
h2{margin:0;font-size:24px}a{color:#175ca1}.diagram{overflow:auto;padding:20px 0}
.diagram img{display:block;margin:auto;max-width:100%;height:auto}li{margin:8px 0;color:#46566a}
@media(max-width:900px){nav{position:static;width:auto}main{margin:0;padding:18px}}
@media print{nav{display:none}main{margin:0;padding:0}section{break-before:page;border:0}.diagram{overflow:visible}}
</style><nav><strong>CATALOG_TITLE</strong>''' + ''.join(nav) + f'''</nav>
<main><h1>{title_html}</h1><p>{len(items)} vistas · SVG integrados · lectura sin conexión</p>
<p>{subtitle_html}</p>''' + ''.join(cards) + '</main></html>'
    (root / 'offline.html').write_text(page.replace('CATALOG_TITLE', title_html))
    print(f'Generated {len(items)} SVGs, diagrams.md and offline.html')


if __name__ == '__main__':
    main()
