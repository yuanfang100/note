from urllib.request import Request, urlopen

url = "https://rag.docs-hub.com/html/2.milvus.html"
req = Request(
    url,
    headers={"User-Agent": "Mozilla/5.0"},
    method="GET",
)

with urlopen(req, timeout=10) as resp:
    print("status:", resp.status)
    data = resp.read(200)
    print("first_bytes:", data[:80])
