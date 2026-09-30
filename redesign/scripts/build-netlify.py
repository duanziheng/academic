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
old_image = "https://zihengduan.cn/media/icon_hu0b7a4cb9992c9ac0e91bd28ffd38dd00_9727_512x512_fill_lanczos_center_2.png"
for path in out.rglob("*.html"):
    text = path.read_text().replace(old_image, "https://zihengduan.cn/assets/portrait.jpg")
    text = text.replace("/assets/app.js?v=20260925-audit", "/assets/app.js?v=20260929-research")
    path.write_text(text)
subprocess.run([sys.executable, str(ROOT / "scripts/render-research.py"), str(out)], check=True)
print("Netlify output:", out)
subprocess.run([sys.executable, str(ROOT / "scripts/check-site.py"), str(out)], check=True)
