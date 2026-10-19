#!/usr/bin/env python3
"""Create the sharing-kit QR code for any registered state that does not have one.

Existing QR files are never overwritten, so printed flyers stay valid.
Requires the qrcode package: pip install qrcode
"""
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from state_registry import BASE_URL, ROOT, load_registry  # noqa: E402

try:
    import qrcode
    import qrcode.image.svg
except ImportError:
    sys.exit('Install the qrcode package first: pip install qrcode')


def main():
    made = []
    for state in load_registry(ROOT):
        target = ROOT / state['qr']
        if target.exists():
            continue
        # Point at the canonical single-page address; legacy state pages only redirect there.
        url = BASE_URL if state.get('base') else BASE_URL + '?state=' + state['code']
        code = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=4,
                             image_factory=qrcode.image.svg.SvgPathImage)
        code.add_data(url)
        code.make(fit=True)
        buffer = io.BytesIO()
        code.make_image().save(buffer)
        target.write_bytes(buffer.getvalue())
        made.append(f"{state['code']}: {target.relative_to(ROOT)} -> {url}")
    print('\n'.join(made) if made else 'Every registered state already has a QR code.')


if __name__ == '__main__':
    main()
