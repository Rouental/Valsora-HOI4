# Mockup source: the original design boards

These are the six boards of the original Valsora art deco mockup, saved as standalone HTML/CSS pages.
Each is a 1920x1080 screen. `../*.jpg` are renders of exactly these pages.

| File | Board |
|---|---|
| `Main.html` | In-game HUD: Rouental, 1 March 1936 (top bar, tooltip, outliner, map) |
| `Government.html` | Government (politics) screen, with The Court scripted panel |
| `MainMenu.html` | Main menu |
| `FocusTree.html` | National focus: Rouentaise tree |
| `Superevent.html` | Superevent: The Rouentaise Civil War |
| `SpriteKit.html` | Sprite kit: panels, buttons, type, focus states, icons, palette (what gets exported to .dds) |

Open a file in a Chromium-based browser at 1920x1080, or render it:

```python
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1920, "height": 1080})
    pg.goto("file:///<path>/art/mockups/source/Main.html"); pg.wait_for_timeout(800)
    pg.screenshot(path="Main.png"); b.close()
```

- Images are in `assets/`: Valsora flags, leader portraits, the Rouental map backdrop, the world
  map for the menu and the superevent picture.
- Fonts load from the project's `source_fonts/` (three folders up). Keep the folder structure intact.
- The pages are static. The `<x-dc>`, `<helmet>` and `text/x-dc` tags are leftovers from the
  design tool and can be ignored.
- These are design targets, not game files. Nothing here is loaded by HOI4.
