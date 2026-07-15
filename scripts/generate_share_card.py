#!/usr/bin/env python3
"""Generate a 1080x1080 share card PNG from profile.yaml.

Usage:
    python3 scripts/generate_share_card.py --profile data/users/yuma/profile.yaml \
      --output output/share/yuma.png
"""
import argparse
import os
import sys as _sys
from pathlib import Path as _Path

_sys.path.insert(0, str(_Path(__file__).resolve().parent.parent))
from jinja2 import Template
from playwright.sync_api import sync_playwright
from sections import _get_archetype, _get_share_tagline, load_yaml

TEMPLATE_PATH = _Path(__file__).resolve().parent.parent / 'templates' / 'share_card.html'


def render_card_html(p: dict) -> str:
    archetype = _get_archetype(p)
    tagline = _get_share_tagline(p)
    template = Template(TEMPLATE_PATH.read_text())
    return template.render(
        archetype_en=archetype['en'],
        archetype_ja=archetype['ja'],
        share_tagline=tagline,
    )


def render_card_png(html: str, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width': 1080, 'height': 1080}, device_scale_factor=2)
        page.set_content(html, wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        page.screenshot(path=output_path, clip={'x': 0, 'y': 0, 'width': 1080, 'height': 1080})
        browser.close()


def main():
    parser = argparse.ArgumentParser(description='Generate Self-Insight share card PNG')
    parser.add_argument('--profile', required=True, help='Path to profile.yaml')
    parser.add_argument('--output', required=True, help='Output PNG path')
    args = parser.parse_args()

    profile = load_yaml(args.profile)
    html = render_card_html(profile)
    render_card_png(html, args.output)
    print(f'Share card written to {args.output}')


if __name__ == '__main__':
    main()
