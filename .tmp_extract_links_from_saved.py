from pathlib import Path
from typing import List, Set
from urllib.parse import urljoin, urldefrag
from lxml import html
import re

saved_path = Path("../../珠峰/AI课/web-site/rag.docs/html/1.vector.html")
base_url = "https://rag.docs-hub.com/html/1.vector.html"

raw = saved_path.read_text(encoding="utf-8", errors="ignore")
doc = html.fromstring(raw)

# 复用当前 rag.docs.py 的提取规则（只抽取 a/link/script/img 等 + style url(...)）
attrs_selectors = [
    ("//a[@href]/@href",),
    ("//link[@href]/@href",),
    ("//script[@src]/@src",),
    ("//img[@src]/@src",),
    ("//iframe[@src]/@src",),
    ("//source[@src]/@src",),
    ("//video[@src]/@src",),
    ("//audio[@src]/@src",),
]

links: List[str] = []
for (xpath,) in attrs_selectors:
    for v in doc.xpath(xpath):
        if isinstance(v, str) and v.strip():
            links.append(v.strip())

style_texts: List[str] = []
style_texts.extend(doc.xpath("//style/text()"))
style_texts.extend(doc.xpath('//*[@style]/@style'))

for t in style_texts:
    if not t:
        continue
    for m in re.findall(r'url\((["\']?)([^"\')]+)\1\)', t):
        if isinstance(m, tuple) and len(m) == 2:
            u = m[1].strip()
            if u:
                links.append(u)

abs_links: List[str] = []
for href in links:
    if href.startswith("javascript:") or href.startswith("mailto:") or href.startswith("tel:"):
        continue
    abs_links.append(urljoin(base_url, href))

dedup: List[str] = []
seen: Set[str] = set()
for u in abs_links:
    u2 = urldefrag(u)
    if u2 not in seen:
        seen.add(u2)
        dedup.append(u2)

target = "https://rag.docs-hub.com/html/2.milvus.html"
print("total_unique_links:", len(dedup))
print("has_target(2.milvus html):", target in dedup)
# 同时打印一些包含 milvus 的链接（最多前 20 个）
milvus = [u for u in dedup if "milvus" in u]
print("milvus_links_count:", len(milvus))
print("milvus_links_sample:", milvus[:20])
