"""Post-CapCut-session failproof pass (spec CINDY_REEL_FACTORY.md section 7b).
Waits for CapCut to close, then: re-grafts paper texts if blanked, fixes track order,
applies pending segment trims, syncs the mirror, and verifies. Reusable per-draft.
Usage: python post_session_fix.py <draft-folder> <video-name>
  e.g.: python post_session_fix.py "<your drafts dir>/CZ_Topic_20260801_v1" Topic
(drafts dir: Windows %LOCALAPPDATA%/CapCut Drafts, macOS ~/Movies/CapCut/User Data/
Projects/com.lveditor.draft - `capcut doctor` prints it.)
<video-name> selects _state/<video-name>_paper_text_map.json. STATE and _backups
resolve relative to this script's own location; works on Windows, macOS, and Linux."""
import json, time, copy, shutil, subprocess, sys, os

STATE = os.path.dirname(os.path.abspath(__file__))          # .../CindyPipeline/_state
BACKUPS = os.path.join(os.path.dirname(STATE), "_backups")  # .../CindyPipeline/_backups
DRAFT_DIR = sys.argv[1] if len(sys.argv) > 1 else r"EDIT_ME__full_path_to_draft_folder"
_VIDEO = sys.argv[2] if len(sys.argv) > 2 else "EDIT_ME__video_name"
CANON = os.path.join(DRAFT_DIR, "template-2.tmp")
MIRROR = os.path.join(DRAFT_DIR, "draft_content.json")
if not os.path.isfile(CANON):
    CANON = MIRROR  # older CapCut: draft_content.json IS canonical (no mirror file)
DONOR = os.path.join(STATE, "paper_donor_child.json")
TEXTMAP = os.path.join(STATE, _VIDEO + "_paper_text_map.json")
# pending one-off fixes: segment-id-prefix -> target duration (seconds)
PENDING_TRIMS = {}  # add segment-id-prefix -> seconds when needed
BASE_LEN, BASE_W = 12.0, 394.6457824707031
US = 1_000_000

if not os.path.isdir(DRAFT_DIR) or not os.path.isfile(TEXTMAP):
    print("CONFIG ERROR: draft folder or text map not found.")
    print("  draft :", DRAFT_DIR)
    print("  map   :", TEXTMAP)
    print("Pass both as args: python post_session_fix.py <draft-folder> <video-name>")
    sys.exit(2)

def capcut_running():
    try:
        if os.name == "nt":
            # tasklist prints image names only (never our own args), so no self-match
            out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
            return "capcut" in out.lower()
        # macOS/Linux: exact-name match; -f would self-match this script's own
        # command line (the draft path argument contains "CapCut")
        out = subprocess.run(["pgrep", "-ix", "CapCut"], capture_output=True, text=True).stdout
        return bool(out.strip())
    except FileNotFoundError:
        print("WARNING: cannot check the process list on this OS - make sure CapCut is closed.")
        return False

def log(*a): print(*a, flush=True)

# 1. wait for CapCut to close (max 4h)
waited = 0
while capcut_running():
    if waited == 0: log("CapCut is running - waiting for it to close...")
    time.sleep(20); waited += 20
    if waited > 4*3600: log("TIMEOUT: CapCut still open after 4h; aborting safely."); sys.exit(1)
if waited: log(f"CapCut closed after {waited}s.")
time.sleep(5)  # let its final autosave settle

stamp = time.strftime("%Y%m%d_%H%M%S")
shutil.copyfile(CANON, os.path.join(BACKUPS, f"postsession_{stamp}.tmp"))

donor = json.load(open(DONOR, encoding="utf-8"))
textmap = json.load(open(TEXTMAP, encoding="utf-8"))
d = json.load(open(CANON, encoding="utf-8"))
mats = d["materials"]
texts_by_id = {m["id"]: m for m in mats["texts"]}
tts = {m["id"]: m for m in mats["text_templates"]}

regrafted = trimmed = 0
for tr in d["tracks"]:
    for seg in tr["segments"]:
        k = seg["id"].lower()[:8]
        # pending trims
        if k in PENDING_TRIMS:
            dur = int(PENDING_TRIMS[k]*US)
            if seg["target_timerange"]["duration"] != dur:
                seg["target_timerange"]["duration"] = dur
                if seg.get("source_timerange"):
                    seg["source_timerange"]["duration"] = dur
                trimmed += 1
        # paper text re-graft if blanked
        if k in textmap:
            tt = tts.get(seg.get("material_id"))
            if not tt: continue
            r = tt["text_info_resources"][0]
            ch = texts_by_id.get(r["text_material_id"])
            want = textmap[k]
            cur = None
            if ch and ch.get("content"):
                try: cur = json.loads(ch["content"]).get("text")
                except Exception: cur = None
            if cur != want and ch is not None:
                g = copy.deepcopy(donor); g["id"] = ch["id"]
                c = json.loads(g["content"]); c["text"] = want
                for st in c.get("styles", []):
                    if isinstance(st.get("range"), list) and len(st["range"]) == 2:
                        st["range"] = [0, len(want)]
                g["content"] = json.dumps(c, ensure_ascii=False)
                ch.clear(); ch.update(g)
                r["attach_info"]["original_size_width"] = BASE_W*max(0.5, min(2.0, len(want)/BASE_LEN))
                dur = seg["target_timerange"]["duration"]
                for wk in ("origin_word_info", "current_word_info"):
                    wi = tt.get(wk)
                    if isinstance(wi, dict):
                        wi["text"] = want; wi["start_time"] = 0; wi["end_time"] = dur
                regrafted += 1

# track order: V1 first, adjust second
v1 = adj = None; others = []
for tr in d["tracks"]:
    if tr.get("type") == "video" and v1 is None and tr["segments"] and not tr.get("name"):
        v1 = tr
    elif tr.get("type") == "adjust": adj = tr
    else: others.append(tr)
reordered = False
if v1 and adj:
    new_order = [v1, adj] + others
    if new_order != d["tracks"]:
        d["tracks"] = new_order; reordered = True
    for i, tr in enumerate(d["tracks"]):
        for seg in tr["segments"]:
            if seg.get("track_render_index") != i:
                seg["track_render_index"] = i; reordered = True

json.dump(d, open(CANON, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
if CANON != MIRROR:
    shutil.copyfile(CANON, MIRROR)
log(f"re-grafted: {regrafted} | trims applied: {trimmed} | track order fixed: {reordered}")

lint = subprocess.run(["capcut", "lint", DRAFT_DIR], capture_output=True, text=True, shell=True).stdout
try:
    lj = json.loads(lint); log("lint errors:", len(lj.get("errors", [])), "warnings:", len(lj.get("warnings", [])))
except Exception: log("lint raw:", lint[:200])
log("DONE - post-session pass complete.")
