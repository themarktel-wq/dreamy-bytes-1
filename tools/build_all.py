"""Rebuild everything: products, website, brand assets."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_products, build_site
build_products.main()
build_site.main()
try:
    import build_brand
    build_brand.main()
    import shutil
    shutil.copy(os.path.join(HERE, "..", "brand", "banners", "og-website-1200x630.png"), os.path.join(HERE, "..", "website", "assets", "og.png"))
except Exception as e:  # Playwright/Node not installed
    print("Skipped brand render:", e)
