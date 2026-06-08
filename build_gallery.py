#!/usr/bin/env python3
"""Regenerate gallery.html and index.html from the images/ folder + categories.json.
- images/ folder = source of truth for which images exist.
- categories.json = {filename: "poll"|"other"} classification.
- New images not present in categories.json default to "poll" and are added to categories.json.
Run: python3 build_gallery.py
"""
import os, re, json, unicodedata

ROOT=os.path.dirname(os.path.abspath(__file__))
IMG=os.path.join(ROOT,"images")
CATS=os.path.join(ROOT,"categories.json")
IMG_EXT={".jpg",".jpeg",".png",".gif",".webp",".heic"}
DEFAULT_LABEL="poll"   # new images default to アンケート

def jsstr(s):
    return s.replace("\\","\\\\").replace('"','\\"')

# 1) gather image files (NFC), sorted
names=[]
for f in os.listdir(IMG):
    if os.path.splitext(f)[1].lower() in IMG_EXT:
        names.append(unicodedata.normalize("NFC", f))
names=sorted(set(names))

# 2) load categories, apply default for new
cats={}
if os.path.exists(CATS):
    cats={unicodedata.normalize("NFC",k):v for k,v in json.load(open(CATS,encoding="utf-8")).items()}
changed=False
labels={}
for n in names:
    lab=cats.get(n)
    if lab not in ("poll","other"):
        lab=DEFAULT_LABEL; changed=True
    labels[n]=lab
# prune categories for images that no longer exist, keep existing decisions
new_cats={n:labels[n] for n in names}
if new_cats!=cats:
    json.dump(new_cats, open(CATS,"w",encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)

# 3) build ALL_IMAGES + CAT_BY_IDX
all_lines=[]
cat_arr=[]
for idx,n in enumerate(names):
    all_lines.append('  {name: "%s", src: "images/" + encodeURIComponent("%s"), idx: %d},'
                     % (jsstr(n), jsstr(n), idx))
    cat_arr.append(labels[n])
poll=sum(1 for n in names if labels[n]=="poll")
other=sum(1 for n in names if labels[n]=="other")
total=len(names)

# 4) fill templates
gt=open(os.path.join(ROOT,"gallery.template.html"),encoding="utf-8").read()
gt=gt.replace("__ALL_IMAGES__", "\n".join(all_lines))
gt=gt.replace("__CAT_BY_IDX__", json.dumps(cat_arr,separators=(",",":")))
gt=gt.replace("__POLL__", str(poll)).replace("__OTHER__", str(other)).replace("__TOTAL__", str(total))
open(os.path.join(ROOT,"gallery.html"),"w",encoding="utf-8").write(gt)

it=open(os.path.join(ROOT,"index.template.html"),encoding="utf-8").read()
it=it.replace("__POLL__", str(poll)).replace("__OTHER__", f"{other:,}")
open(os.path.join(ROOT,"index.html"),"w",encoding="utf-8").write(it)

print(f"built: total={total} poll={poll} other={other}  (categories.json {'updated' if new_cats!=cats else 'unchanged'})")
