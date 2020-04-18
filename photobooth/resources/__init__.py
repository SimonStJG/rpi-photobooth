from pathlib import Path

resources_root = Path(__file__).parent
stylesheets_root = resources_root / "stylesheets"
images_root = resources_root / "images"
ui_root = resources_root / "ui"
fonts_root = resources_root / "fonts"


__all__ = [
    stylesheets_root,
    images_root,
    ui_root,
    fonts_root,
]
