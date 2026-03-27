import os, json, glob

MY_DATASETS = ["adm","biggan","glide","midjourney",
               "sd_v1_4","sd_v1_5","vqdm","wukong"]

base = "outputs"
rows = []

for ds in MY_DATASETS:
    root = os.path.join(base, f"eval_{ds}")
    if not os.path.isdir(root):
        print(f"[WARN] Missing folder: {root}")
        continue

    jsons = glob.glob(os.path.join(root, "**", "*.json"),
                      recursive=True)

    if not jsons:
        print(f"[WARN] No JSON found under {root}")
        continue

    jpath = jsons[0]

    with open(jpath) as f:
        data = json.load(f)

    if isinstance(next(iter(data.values())), dict):
        m = next(iter(data.values()))
    else:
        m = data

    rows.append([
        ds,
        m["accuracy"],
        m["f1_score"],
        m["auroc"],
        m["precision"],
        m["recall"]
    ])

print("\n===== SWIN GENIMAGE RESULTS =====\n")
print(f"{'Dataset':15} {'Acc':>8} {'F1':>8} {'AUROC':>8} {'Prec':>8} {'Recall':>8}")
print("-"*65)

for r in rows:
    print(f"{r[0]:15} {r[1]:8} {r[2]:8} {r[3]:8} {r[4]:8} {r[5]:8}")
