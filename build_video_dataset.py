"""Build a deduplicated daily dataset from the raw Yuntu snapshots.

Raw files are read-only. A same-day material is represented by the record with the
largest exact impression count, following 00_说明.md. Absence from the daily top
6000 is kept as missing; no zero filling is performed.
"""
from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools" / "pydeps"))
import ijson  # noqa: E402

DATA = ROOT / "data"
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

FIELDS = [
    "date", "period", "rank", "material_uri", "material_id", "title",
    "impressions", "clicks", "conversions", "ctr", "cvr", "pvr",
    "play_3s_rate", "play_5s_rate", "play_over_rate", "play_duration_avg",
    "interact_rate", "interact_cnt", "like_rate", "comment_rate", "share_rate",
    "video_duration", "publish_time", "keywords", "people_tags", "material_tags",
    "product_name", "product_cate", "price_range",
]


def as_float(value) -> float:
    try:
        if value is None or value == "":
            return 0.0
        result = float(value)
        return result if math.isfinite(result) else 0.0
    except (TypeError, ValueError):
        return 0.0


def as_int(value) -> int:
    return int(round(as_float(value)))


def tag_names(entries, key) -> list[str]:
    names = []
    for entry in entries or []:
        for name in entry.get(key) or []:
            name = str(name).strip()
            if name and name not in names:
                names.append(name)
    return names


def period_for(day: str) -> str:
    # The 84-day window is exactly three non-overlapping 28-day periods.
    if day <= "20260907":
        return "P1_20260811_20260907"
    if day <= "20261005":
        return "P2_20260908_20261005"
    return "P3_20261006_20261102"


def normalize(item, day: str) -> dict:
    idx = item.get("object_index") or {}
    impressions = as_int(idx.get("show_cnt"))
    ctr = as_float(idx.get("ctr"))
    cvr = as_float(idx.get("cvr"))
    pvr = as_float(idx.get("pvr"))
    clicks = int(round(impressions * ctr))
    # pvr is empirically identical to ctr*cvr in the raw interface. Using the
    # impression-level product avoids compounding rounded click estimates.
    conversions = int(round(impressions * pvr))
    products = item.get("product_info_list") or []
    product = products[0] if products else {}
    return {
        "date": datetime.strptime(day, "%Y%m%d").strftime("%Y-%m-%d"),
        "period": period_for(day),
        "material_uri": str(item.get("material_uri") or ""),
        "material_id": str(item.get("material_id") or item.get("item_id") or ""),
        "title": str(item.get("title") or ""),
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "ctr": ctr,
        "cvr": cvr,
        "pvr": pvr,
        "play_3s_rate": as_float(idx.get("play_3s_rate")),
        "play_5s_rate": as_float(idx.get("play_5s_rate")),
        "play_over_rate": as_float(idx.get("play_over_rate")),
        "play_duration_avg": as_float(idx.get("play_duration_avg")),
        "interact_rate": as_float(idx.get("interact_rate")),
        "interact_cnt": as_int(idx.get("interact_cnt")),
        "like_rate": as_float(idx.get("like_rate")),
        "comment_rate": as_float(idx.get("comment_rate")),
        "share_rate": as_float(idx.get("share_rate")),
        "video_duration": as_float(item.get("video_duration")),
        "publish_time": str(idx.get("publish_time") or idx.get("create_time") or ""),
        "keywords": "|".join(str(x) for x in item.get("keywords") or []),
        "people_tags": "|".join(tag_names(item.get("people_tag_entry"), "tag_name_list")),
        "material_tags": "|".join(tag_names(item.get("material_tag_entry"), "tag_name_list")),
        "product_name": str(product.get("product_name") or ""),
        "product_cate": str(product.get("cate_name") or ""),
        "price_range": str(product.get("price_range") or ""),
        "_identity_error": abs(ctr * cvr - pvr),
    }


def main() -> None:
    daily_path = OUT / "video_daily.csv.gz"
    metadata = {}
    totals = defaultdict(int)
    daily_counts = {}
    identity_errors = []
    bad_uri_rows = 0

    with gzip.open(daily_path, "wt", encoding="utf-8-sig", newline="") as out_fh, \
            (DATA / "industry17_daily84.json").open("rb") as main_fh:
        writer = csv.DictWriter(out_fh, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for day, main_items in ijson.kvitems(main_fh, ""):
            totals["main_raw_rows"] += len(main_items)
            deep_path = DATA / "industry17_deep" / f"{day}.json"
            deep_items = json.loads(deep_path.read_text(encoding="utf-8"))["items"]
            totals["deep_raw_rows"] += len(deep_items)
            best = {}
            for source, items in (("main", main_items), ("deep", deep_items)):
                for item in items:
                    rec = normalize(item, day)
                    uri = rec["material_uri"]
                    if not uri:
                        bad_uri_rows += 1
                        continue
                    identity_errors.append(rec["_identity_error"])
                    previous = best.get(uri)
                    if previous is None:
                        best[uri] = rec
                    else:
                        totals["duplicate_rows_removed"] += 1
                        if rec["impressions"] > previous["impressions"]:
                            best[uri] = rec
            ordered = sorted(best.values(), key=lambda x: x["impressions"], reverse=True)
            daily_counts[day] = len(ordered)
            for rank, rec in enumerate(ordered, 1):
                rec["rank"] = rank
                writer.writerow(rec)
                uri = rec["material_uri"]
                if uri not in metadata:
                    metadata[uri] = {
                        "material_uri": uri,
                        "material_id": rec["material_id"],
                        "title": rec["title"],
                        "first_day": rec["date"],
                        "last_day": rec["date"],
                        "days": 0,
                        "impressions": 0,
                        "clicks": 0,
                        "conversions": 0,
                        "product_name": rec["product_name"],
                        "product_cate": rec["product_cate"],
                    }
                meta = metadata[uri]
                meta["days"] += 1
                meta["last_day"] = rec["date"]
                for field in ("impressions", "clicks", "conversions"):
                    meta[field] += rec[field]
                if rec["title"]:
                    meta["title"] = rec["title"]
                if rec["product_name"]:
                    meta["product_name"] = rec["product_name"]
                    meta["product_cate"] = rec["product_cate"]
            totals["deduplicated_rows"] += len(ordered)
            print(day, len(main_items), len(deep_items), len(ordered), flush=True)

    summary_path = OUT / "material_totals.csv"
    with summary_path.open("w", encoding="utf-8-sig", newline="") as fh:
        fields = ["material_uri", "material_id", "title", "first_day", "last_day", "days",
                  "impressions", "clicks", "conversions", "product_name", "product_cate"]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(metadata.values())

    quality = {
        "raw_main_rows": totals["main_raw_rows"],
        "raw_deep_rows": totals["deep_raw_rows"],
        "duplicate_rows_removed": totals["duplicate_rows_removed"],
        "deduplicated_rows": totals["deduplicated_rows"],
        "unique_materials": len(metadata),
        "days": len(daily_counts),
        "daily_rows_min": min(daily_counts.values()),
        "daily_rows_max": max(daily_counts.values()),
        "days_not_6000": [day for day, count in daily_counts.items() if count != 6000],
        "rows_with_blank_material_uri": bad_uri_rows,
        "max_abs_ctr_cvr_minus_pvr": max(identity_errors) if identity_errors else None,
        "mean_abs_ctr_cvr_minus_pvr": sum(identity_errors) / len(identity_errors) if identity_errors else None,
        "total_impressions": sum(x["impressions"] for x in metadata.values()),
        "total_clicks": sum(x["clicks"] for x in metadata.values()),
        "total_conversions": sum(x["conversions"] for x in metadata.values()),
        "daily_file": str(daily_path),
        "material_totals_file": str(summary_path),
    }
    (OUT / "extraction_quality.json").write_text(
        json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(quality, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
