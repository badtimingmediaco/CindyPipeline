#!/usr/bin/env python3
"""Tenor meme sourcing WITHOUT an API key.

Why this exists: the spec's documented route (Tenor v1 API + the public demo key
LIVDSRZULELA) is dead - v1 returns 403 on both g.tenor.com and api.tenor.com, and
v2 rejects the demo key. This uses tenor.com's own server-rendered pages instead:

  1. GET https://tenor.com/search/<slug>-gifs   -> ~49 /view/ links in the raw HTML
  2. GET https://tenor.com/view/<...>           -> <meta property="og:video"> = the MP4
  3. download that MP4

The og:video URL is always the MP4 (media id suffix AAAPo, typically 640px wide),
which satisfies the MP4-not-GIF rule in section 4.3. No API key, no browser needed.

Usage:
  python tenor_fetch.py "charlie day conspiracy board" --n 3 --out <dir> --prefix m5
  python tenor_fetch.py --queries queries.json --out <dir>
"""
import json, os, re, sys, urllib.request, urllib.parse, time

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
VIEW_RE = re.compile(r'href="(/view/[^"]+)"')
# NOTE: the meta tag carries class="dynamic" BEFORE property= - do not anchor on
# '<meta property=' or you will silently find nothing.
def meta(html, prop):
    m = re.search(r'<meta[^>]*property="%s"[^>]*content="([^"]+)"' % re.escape(prop), html)
    if not m:
        m = re.search(r'<meta[^>]*content="([^"]+)"[^>]*property="%s"' % re.escape(prop), html)
    return m.group(1) if m else None


def get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout).read()


def get_text(url, timeout=25):
    return get(url, timeout).decode("utf-8", "ignore")


def search(query, limit=12):
    """Return up to `limit` candidate dicts for a query."""
    slug = urllib.parse.quote(re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-"))
    html = get_text(f"https://tenor.com/search/{slug}-gifs")
    views = list(dict.fromkeys(VIEW_RE.findall(html)))
    out = []
    for v in views[:limit]:
        try:
            page = get_text("https://tenor.com" + v)
        except Exception as e:
            continue
        mp4 = meta(page, "og:video") or meta(page, "og:video:secure_url")
        if not mp4 or not mp4.endswith(".mp4"):
            continue          # section 4.3: never fall back to the .gif - skip it
        out.append({
            "view": "https://tenor.com" + v,
            "mp4": mp4,
            "title": meta(page, "og:title") or "",
            "width": int(meta(page, "og:video:width") or 0),
            "height": int(meta(page, "og:video:height") or 0),
            "slug": v.rsplit("/", 1)[-1],
        })
        time.sleep(0.15)      # be polite
    return out


def download(url, dest):
    data = get(url, timeout=60)
    with open(dest, "wb") as f:
        f.write(data)
    return os.path.getsize(dest)


def fetch_slot(queries, out_dir, prefix, per_query=3, want=3):
    """Audition candidates for one meme slot across several query variants."""
    os.makedirs(out_dir, exist_ok=True)
    got, seen = [], set()
    for q in queries:
        try:
            cands = search(q, limit=per_query * 3)
        except Exception as e:
            print(f"    ! query {q!r} failed: {type(e).__name__} {e}")
            continue
        taken = 0
        for c in cands:
            if c["mp4"] in seen:
                continue
            seen.add(c["mp4"])
            name = f"{prefix}_{len(got):02d}_{re.sub(r'[^a-z0-9]+','_',c['slug'].lower())[:40]}.mp4"
            dest = os.path.join(out_dir, name)
            try:
                size = download(c["mp4"], dest)
            except Exception as e:
                print(f"    ! download failed: {e}")
                continue
            c["file"] = dest
            c["bytes"] = size
            try:
                import subprocess as _sp
                dur = float(_sp.run(["ffprobe","-v","error","-show_entries","format=duration",
                                     "-of","csv=p=0",dest],capture_output=True,text=True).stdout.strip() or 0)
                c["duration"] = round(dur, 3)
                if dur < 0.5:            # Tenor serves many single-frame 0.04s clips
                    os.remove(dest)
                    print(f"    - discarded {os.path.basename(dest)} ({dur:.2f}s single-frame)")
                    continue
            except Exception:
                c["duration"] = None
            c["query"] = q
            got.append(c)
            taken += 1
            if taken >= per_query or len(got) >= want:
                break
        if len(got) >= want:
            break
    return got


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    out = "."
    if "--out" in args:
        out = args[args.index("--out") + 1]
    want = int(args[args.index("--want") + 1]) if "--want" in args else 3
    if args[0] == "--queries":
        spec = json.load(open(args[1], encoding="utf-8"))
        result = {}
        for slot, queries in spec.items():
            print(f"[{slot}] {queries}")
            result[slot] = fetch_slot(queries, os.path.join(out, slot), slot,
                                      per_query=max(3, want // max(1, len(queries)) + 1),
                                      want=want)
            for c in result[slot]:
                print(f"    {os.path.basename(c['file'])}  {c['width']}x{c['height']}  {c['title'][:50]!r}")
        json.dump(result, open(os.path.join(out, "candidates.json"), "w",
                               encoding="utf-8"), indent=1)
    else:
        n = int(args[args.index("--n") + 1]) if "--n" in args else 3
        pre = args[args.index("--prefix") + 1] if "--prefix" in args else "cand"
        for c in fetch_slot([args[0]], out, pre, want=n):
            print(json.dumps(c, indent=1))
