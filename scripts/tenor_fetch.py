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


class ScrapeShapeError(RuntimeError):
    """Tenor's HTML no longer looks the way this scraper expects.

    Raised - loudly - rather than returning nothing. The silent empty result is the
    dangerous failure mode: the build carries on, places no meme on that beat, and
    nobody notices until someone watches the reel. If you see this, re-derive the
    selectors against a live page before changing anything else.
    """


def get(url, timeout=25, tries=3):
    """GET with backoff. Tenor rate-limits and occasionally 502s under a burst, and a
    single attempt turns a momentary blip into a permanently missing meme."""
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return urllib.request.urlopen(req, timeout=timeout).read()
        except Exception as e:
            last = e
            if getattr(e, "code", None) in (400, 404, 410):   # permanent; retry is futile
                raise
            if i < tries - 1:
                time.sleep(1.5 * (2 ** i))                    # 1.5s, then 3s
    raise last


def get_text(url, timeout=25):
    return get(url, timeout).decode("utf-8", "ignore")


def search(query, limit=12):
    """Return up to `limit` candidate dicts for a query.

    Raises ScrapeShapeError when the search page yields no /view/ links at all: that
    means the page shape changed or we were blocked, NOT that the query had no hits.
    A genuinely empty query still renders a page full of related links.
    """
    slug = urllib.parse.quote(re.sub(r"[^a-z0-9]+", "-", query.lower()).strip("-"))
    html = get_text(f"https://tenor.com/search/{slug}-gifs")
    views = list(dict.fromkeys(VIEW_RE.findall(html)))
    if not views:
        raise ScrapeShapeError(
            f"no /view/ links on the search page for {query!r} ({len(html)} bytes). "
            "Tenor changed its markup, or the request was blocked. "
            "Run `python tenor_fetch.py --selftest` to tell those apart.")
    out = []
    for v in views[:limit]:
        try:
            page = get_text("https://tenor.com" + v)
        except Exception:
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
    shape_errors = 0
    for q in queries:
        try:
            cands = search(q, limit=per_query * 3)
        except ScrapeShapeError as e:
            shape_errors += 1
            print(f"    !! SCRAPE SHAPE: {e}")
            continue
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

    # Every query failing on SHAPE is not "no good memes for this beat" - it is the
    # scraper being broken. Do not let the build quietly continue with an empty slot.
    if not got and shape_errors and shape_errors == len(queries):
        raise ScrapeShapeError(
            f"all {len(queries)} queries for this slot failed on page shape. "
            "The scraper is broken, not the beat. Fix it before continuing the build.")
    if not got:
        print(f"    ! NOTHING FOUND for this slot after {len(queries)} queries - "
              "this beat will have no meme unless you widen the brief")
    return got


def selftest():
    """Prove each link in the scrape chain still holds, and say which one broke.

    Worth running before a build and any time a slot comes back empty: it separates
    "Tenor redesigned the page" from "that query genuinely has nothing" from "this
    machine has no internet", which otherwise all look identical from inside a build.
    """
    steps = []

    def step(name, fn):
        try:
            ev = fn()
            steps.append((True, name, ev))
            print(f"  [PASS] {name}\n         {ev}")
            return True
        except Exception as e:
            steps.append((False, name, f"{type(e).__name__}: {e}"))
            print(f"  [FAIL] {name}\n         {type(e).__name__}: {e}")
            return False

    print("\nTENOR SCRAPE SELF-TEST\n" + "=" * 60)
    if not step("reach tenor.com", lambda: f"{len(get_text('https://tenor.com'))} bytes"):
        print("\nNo connection to Tenor. Check the network or the VPN.\n")
        return 1

    holder = {}

    def do_search():
        slug = "confused-math-lady"
        html = get_text(f"https://tenor.com/search/{slug}-gifs")
        views = list(dict.fromkeys(VIEW_RE.findall(html)))
        if not views:
            raise ScrapeShapeError(f"0 /view/ links in {len(html)} bytes - MARKUP CHANGED")
        holder["view"] = views[0]
        return f"{len(views)} /view/ links found (first: {views[0][:60]})"

    if not step("search page yields /view/ links", do_search):
        print("\nThe search-page selector is broken. Re-derive VIEW_RE from a live page.\n")
        return 2

    def do_meta():
        page = get_text("https://tenor.com" + holder["view"])
        mp4 = meta(page, "og:video") or meta(page, "og:video:secure_url")
        if not mp4:
            raise ScrapeShapeError("no og:video meta tag - MARKUP CHANGED")
        if not mp4.endswith(".mp4"):
            raise ScrapeShapeError(f"og:video is not an .mp4: {mp4}")
        holder["mp4"] = mp4
        return mp4

    if not step("view page yields an og:video .mp4", do_meta):
        print("\nThe og:video selector is broken. Note the tag carries class= BEFORE\n"
              "property=, so do not anchor a new pattern on '<meta property='.\n")
        return 3

    step("the mp4 actually downloads",
         lambda: f"{len(get(holder['mp4'], timeout=60))} bytes")

    ok = all(s[0] for s in steps)
    print("=" * 60)
    print("Scrape chain intact - Tenor sourcing is working.\n" if ok
          else "Scrape chain BROKEN - see the failed step above.\n")
    return 0 if ok else 4


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)
    if args[0] == "--selftest":
        sys.exit(selftest())
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
