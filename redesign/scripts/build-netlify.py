"""Build a self-contained Netlify deployment, including large paper PDFs."""
from pathlib import Path
import runpy
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
subprocess.run([sys.executable, str(ROOT / "scripts/test-research.py")], check=True)
runpy.run_path(str(ROOT / "build.py"), run_name="__main__")
out = ROOT / "netlify-dist"
if out.exists():
    shutil.rmtree(out)
shutil.copytree(ROOT / "dist", out)
shutil.copytree(ROOT / "large-assets", out, dirs_exist_ok=True)
subprocess.run([sys.executable, str(ROOT / "scripts/render-research.py"), str(out)], check=True)
# The October 2026 refinements load last, after the research layers, on every page built from the site template.
POLISH = '<link rel="stylesheet" href="/assets/polish.css?v=20261011-1">'
for path in out.rglob("*.html"):
    text = path.read_text()
    if "/assets/style.css?" in text and POLISH not in text:
        path.write_text(text.replace("</head>", POLISH + "</head>", 1))
print("Netlify output:", out)
subprocess.run([sys.executable, str(ROOT / "scripts/check-site.py"), str(out)], check=True)
