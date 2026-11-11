"""Score video-level conversion-efficiency proxies with quality gates and EB shrinkage.

The output is NOT financial ROI: the raw data has no spend, paid GMV, refunds,
margin, creative cost, or incrementality. 'Conversions' are reconstructed platform
conversion-event equivalents, not verified orders.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import beta, spearmanr

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
PRIOR_IMPRESSIONS = 10_000.0


def classify_scope_category(product_cate: str, text: str) -> tuple[str, str]:
    cate = str(product_cate or "")
    t = str(text or "").lower()
    non_3c = ["舒肤佳", "海飞丝", "潘婷", "沐浴露", "洗发水", "洗发露", "护发素", "身体清洁"]
    if any(x.lower() in t for x in non_3c) or any(x in cate for x in ["洗发护发", "身体清洁"]):
        return "明显非3C", "排除"
    rules = [
        ("学习与翻译设备", ["学习机", "早教机", "家教机", "翻译机", "翻译笔", "点读", "教育伴学"]),
        ("充电与手机配件", ["充电宝", "充电器", "充电头", "数据线", "移动电源", "手机壳", "手机膜", "钢化膜", "手机支架", "自拍杆", "支点壳", "保护套", "尾插"]),
        ("电脑外设与游戏硬件", ["鼠标", "键盘", "显示器", "游戏手柄", "电脑外设", "电竞外设", "键鼠", "gpw"]),
        ("影像投影与安防", ["投影仪", "投影", "相机", "摄像头", "监控", "云台", "记录仪", "手持稳定器"]),
        ("音频设备", ["耳机", "音响", "音箱", "声卡", "麦克风", "低音炮", "k歌"]),
        ("智能家电与个护电器", ["吹风机", "剃须刀", "电动牙刷", "扫地机", "闺蜜机", "移动电视", "小度"]),
        ("乐器与音乐硬件", ["吉他", "钢琴", "弹唱琴"]),
        ("网络设备", ["wifi", "路由器", "上网设备", "随身wi"]),
        ("手机平板与整机", ["手机", "iphone", "红米", "redmi", "平板", "笔记本", "电脑主机", "手环"]),
    ]
    for category, words in rules:
        if any(w in t for w in words) or any(w in cate.lower() for w in words):
            return category, "纳入"
    return "其他及待复核3C", "纳入"


def ratio(num: pd.Series, den: pd.Series) -> pd.Series:
    return num.astype(float) / den.replace(0, np.nan).astype(float)


def safe_index(ipm: pd.Series, peer_ipm: pd.Series) -> pd.Series:
    return 100 * ipm / peer_ipm.replace(0, np.nan)


def main() -> None:
    df = pd.read_csv(OUT / "video_daily.csv.gz", low_memory=False)
    for col in ["product_cate", "product_name", "title", "keywords", "material_tags", "people_tags"]:
        df[col] = df[col].fillna("")

    df["funnel_identity_error"] = (df["ctr"] * df["cvr"] - df["pvr"]).abs()
    df["valid_funnel"] = (
        (df["impressions"] > 0)
        & df[["ctr", "cvr", "pvr"]].ge(0).all(axis=1)
        & df[["ctr", "cvr", "pvr"]].le(1).all(axis=1)
        & (df["conversions"] <= df["clicks"])
        & (df["funnel_identity_error"] <= 1e-6)
    )
    df["valid_attention"] = (
        df[["play_3s_rate", "play_5s_rate", "play_over_rate"]].ge(0).all(axis=1)
        & df[["play_3s_rate", "play_5s_rate", "play_over_rate"]].le(1).all(axis=1)
        & (df["play_5s_rate"] <= df["play_3s_rate"])
        & (df["play_over_rate"] <= df["play_5s_rate"])
        & (df["play_duration_avg"] >= 0)
    )

    # Metadata uses all raw rows; scoring uses only valid-funnel rows.
    meta_work = df.sort_values("date").copy()
    for col in ["product_cate", "product_name", "title", "keywords", "material_tags", "people_tags"]:
        meta_work[col] = meta_work[col].replace("", np.nan)
    meta = meta_work.groupby("material_uri", sort=False).agg(
        material_id=("material_id", "last"),
        title=("title", "last"),
        first_day=("date", "min"),
        last_day=("date", "max"),
        raw_days=("date", "nunique"),
        raw_impressions=("impressions", "sum"),
        raw_clicks=("clicks", "sum"),
        raw_conversions=("conversions", "sum"),
        video_duration=("video_duration", "median"),
        publish_time=("publish_time", "last"),
        keywords=("keywords", "last"),
        people_tags=("people_tags", "last"),
        material_tags=("material_tags", "last"),
        product_name=("product_name", "last"),
        product_cate=("product_cate", "last"),
        price_range=("price_range", "last"),
        excluded_days=("valid_funnel", lambda s: int((~s).sum())),
        attention_excluded_days=("valid_attention", lambda s: int((~s).sum())),
    )
    # Category rules use product metadata, title and keywords. Material tags are
    # intentionally excluded here because cross-product tags create false peers.
    combined_text = meta[["title", "keywords", "product_name", "product_cate"]].fillna("").astype(str).agg(" ".join, axis=1)
    classified = [classify_scope_category(cate, text) for cate, text in zip(meta["product_cate"].fillna(""), combined_text)]
    meta["category"] = [x[0] for x in classified]
    meta["scope_status"] = [x[1] for x in classified]
    meta["duration_bucket"] = pd.cut(
        meta["video_duration"], bins=[-np.inf, 15, 30, 60, 120, np.inf],
        labels=["≤15秒", "16–30秒", "31–60秒", "61–120秒", ">120秒"]
    ).astype(str)
    meta["peer_group"] = meta["category"] + " × " + meta["duration_bucket"]

    clean = df[df["valid_funnel"]].copy()
    totals = clean.groupby("material_uri", sort=False).agg(
        scored_days=("date", "nunique"),
        impressions=("impressions", "sum"),
        clicks=("clicks", "sum"),
        conversions=("conversions", "sum"),
        interactions=("interact_cnt", "sum"),
        conversion_days=("conversions", lambda s: int((s > 0).sum())),
    )
    scores = meta.join(totals, how="left")
    for col in ["scored_days", "impressions", "clicks", "conversions", "interactions", "conversion_days"]:
        scores[col] = scores[col].fillna(0)
    scores["conversion_day_rate"] = ratio(scores["conversion_days"], scores["scored_days"]).fillna(0)
    scores["ctr_weighted"] = ratio(scores["clicks"], scores["impressions"]).fillna(0)
    scores["cvr_weighted"] = ratio(scores["conversions"], scores["clicks"]).fillna(0)
    scores["ipm_raw"] = (1000 * ratio(scores["conversions"], scores["impressions"])).fillna(0)

    # Period totals; missing means not observed in the daily top 6000, not zero exposure.
    period = clean.pivot_table(index="material_uri", columns="period", values=["impressions", "clicks", "conversions"], aggfunc="sum", fill_value=0)
    period.columns = [f"{metric}_{p.split('_')[0]}" for metric, p in period.columns]
    scores = scores.join(period, how="left")
    for p in ["P1", "P2", "P3"]:
        for metric in ["impressions", "clicks", "conversions"]:
            col = f"{metric}_{p}"
            if col not in scores:
                scores[col] = 0
            scores[col] = scores[col].fillna(0)
        scores[f"ipm_{p}"] = (1000 * ratio(scores[f"conversions_{p}"], scores[f"impressions_{p}"])).fillna(0)
        scores[f"ctr_{p}"] = ratio(scores[f"clicks_{p}"], scores[f"impressions_{p}"]).fillna(0)

    # Attention metrics are independently quality-gated and exposure-weighted.
    att = df[df["valid_attention"]].copy()
    att["watch_seconds_sum"] = att["play_duration_avg"] * att["impressions"]
    for rate in ["play_3s_rate", "play_5s_rate", "play_over_rate"]:
        att[f"{rate}_sum"] = att[rate] * att["impressions"]
    att_agg = att.groupby("material_uri", sort=False).agg(
        attention_impressions=("impressions", "sum"),
        watch_seconds_sum=("watch_seconds_sum", "sum"),
        play_3s_sum=("play_3s_rate_sum", "sum"),
        play_5s_sum=("play_5s_rate_sum", "sum"),
        play_over_sum=("play_over_rate_sum", "sum"),
    )
    scores = scores.join(att_agg, how="left")
    scores["play_3s_rate_weighted"] = ratio(scores["play_3s_sum"], scores["attention_impressions"])
    scores["play_5s_rate_weighted"] = ratio(scores["play_5s_sum"], scores["attention_impressions"])
    scores["play_over_rate_weighted"] = ratio(scores["play_over_sum"], scores["attention_impressions"])
    scores["avg_watch_seconds"] = ratio(scores["watch_seconds_sum"], scores["attention_impressions"])
    scores["retention_5s_to_3s"] = ratio(scores["play_5s_rate_weighted"], scores["play_3s_rate_weighted"])
    scores["watch_duration_ratio"] = ratio(scores["avg_watch_seconds"], scores["video_duration"]).clip(0, 1)

    # Peer baselines use category x duration. Sparse groups fall back to category.
    global_pvr = scores["conversions"].sum() / scores["impressions"].sum()
    peer = scores.groupby("peer_group").agg(peer_materials=("impressions", "size"), peer_impressions=("impressions", "sum"), peer_conversions=("conversions", "sum"))
    peer["peer_pvr"] = peer["peer_conversions"] / peer["peer_impressions"].replace(0, np.nan)
    cat = scores.groupby("category").agg(category_impressions=("impressions", "sum"), category_conversions=("conversions", "sum"))
    cat["category_pvr"] = cat["category_conversions"] / cat["category_impressions"].replace(0, np.nan)
    scores = scores.join(peer[["peer_materials", "peer_pvr"]], on="peer_group").join(cat[["category_pvr"]], on="category")
    scores["baseline_source"] = np.where((scores["peer_materials"] >= 30) & scores["peer_pvr"].notna(), "品类×时长", "品类")
    scores["baseline_pvr"] = np.where(scores["baseline_source"].eq("品类×时长"), scores["peer_pvr"], scores["category_pvr"])
    scores["baseline_pvr"] = scores["baseline_pvr"].fillna(global_pvr)
    scores["baseline_ipm"] = 1000 * scores["baseline_pvr"]

    def add_eb(frame: pd.DataFrame, k: float, suffix: str = "") -> None:
        alpha0 = k * frame["baseline_pvr"]
        beta0 = k * (1 - frame["baseline_pvr"])
        posterior_alpha = frame["conversions"] + alpha0
        posterior_beta = frame["impressions"] - frame["conversions"] + beta0
        frame[f"eb_pvr{suffix}"] = posterior_alpha / (posterior_alpha + posterior_beta)
        frame[f"lcb90_pvr{suffix}"] = beta.ppf(0.05, posterior_alpha, posterior_beta)
        frame[f"eb_ipm{suffix}"] = 1000 * frame[f"eb_pvr{suffix}"]
        frame[f"lcb90_ipm{suffix}"] = 1000 * frame[f"lcb90_pvr{suffix}"]
        frame[f"eb_index{suffix}"] = safe_index(frame[f"eb_ipm{suffix}"], frame["baseline_ipm"])
        frame[f"conservative_index{suffix}"] = safe_index(frame[f"lcb90_ipm{suffix}"], frame["baseline_ipm"])

    add_eb(scores, PRIOR_IMPRESSIONS)
    scores["recent_ipm_change_vs_P2"] = ratio(scores["ipm_P3"], scores["ipm_P2"]) - 1
    scores["recent_ctr_change_vs_P2"] = ratio(scores["ctr_P3"], scores["ctr_P2"]) - 1
    scores["evidence_tier"] = np.select(
        [
            (scores["impressions"] >= 100_000) & (scores["conversions"] >= 20) & (scores["scored_days"] >= 5),
            (scores["impressions"] >= 20_000) & (scores["conversions"] >= 5) & (scores["scored_days"] >= 2),
        ],
        ["规模证据", "验证证据"], default="证据不足"
    )
    scores["recent_evidence"] = np.select(
        [
            (scores["impressions_P3"] >= 20_000) & (scores["conversions_P3"] >= 5),
            scores["impressions_P3"] > 0,
        ],
        ["近28天足量", "近28天少量"], default="近28天未进榜"
    )
    scores["efficiency_decline_flag"] = (
        (scores["impressions_P2"] >= 20_000) & (scores["impressions_P3"] >= 20_000)
        & (scores["conversions_P2"] >= 5) & (scores["recent_ipm_change_vs_P2"] <= -0.30)
    )
    scores["high_efficiency_flag"] = (scores["eb_index"] >= 120) & (scores["conservative_index"] >= 100)
    scores["priority_flag"] = (
        scores["scope_status"].eq("纳入") & scores["evidence_tier"].eq("规模证据")
        & scores["high_efficiency_flag"] & scores["recent_evidence"].eq("近28天足量")
        & ~scores["efficiency_decline_flag"]
    )
    scores["test_flag"] = (
        scores["scope_status"].eq("纳入") & scores["evidence_tier"].isin(["规模证据", "验证证据"])
        & scores["high_efficiency_flag"] & ~scores["priority_flag"] & ~scores["efficiency_decline_flag"]
    )
    scores["diagnosis"] = np.select(
        [
            (scores["play_3s_rate_weighted"] >= 0.30) & (scores["retention_5s_to_3s"] < 0.55),
            (scores["ctr_weighted"] >= 0.05) & (scores["cvr_weighted"] < 0.02),
            (scores["play_3s_rate_weighted"] < 0.20) & (scores["eb_index"] >= 120),
            scores["efficiency_decline_flag"],
        ],
        ["开场强但5秒承接弱", "点击高但点击后转化弱", "效率好但开场可优化", "近期转化效率衰退"],
        default="按漏斗逐项观察"
    )
    scores["video_url"] = "https://yuntu.oceanengine.com/yuntu_ng/content/shared/video_previewer?code=" + scores.index

    # Temporal split: first 56 days for discovery, final 28 days for descriptive validation.
    scores["train_impressions"] = scores["impressions_P1"] + scores["impressions_P2"]
    scores["train_conversions"] = scores["conversions_P1"] + scores["conversions_P2"]
    period_peer = scores.groupby("peer_group").agg(
        train_peer_impressions=("train_impressions", "sum"),
        train_peer_conversions=("train_conversions", "sum"),
        test_peer_impressions=("impressions_P3", "sum"),
        test_peer_conversions=("conversions_P3", "sum"),
    )
    scores = scores.join(period_peer, on="peer_group")
    scores["train_period_baseline_pvr"] = ratio(scores["train_peer_conversions"], scores["train_peer_impressions"]).fillna(scores["baseline_pvr"])
    scores["test_period_baseline_pvr"] = ratio(scores["test_peer_conversions"], scores["test_peer_impressions"]).fillna(scores["baseline_pvr"])
    train_alpha = scores["train_conversions"] + PRIOR_IMPRESSIONS * scores["train_period_baseline_pvr"]
    train_beta = scores["train_impressions"] - scores["train_conversions"] + PRIOR_IMPRESSIONS * (1 - scores["train_period_baseline_pvr"])
    scores["train_eb_ipm"] = 1000 * train_alpha / (train_alpha + train_beta)
    scores["train_index"] = safe_index(scores["train_eb_ipm"], 1000 * scores["train_period_baseline_pvr"])
    # The test baseline is estimated within P3, removing period-wide seasonality
    # from the descriptive temporal validation.
    scores["test_index_raw"] = safe_index(scores["ipm_P3"], 1000 * scores["test_period_baseline_pvr"])
    train_pool = scores[(scores["scope_status"] == "纳入") & (scores["train_impressions"] >= 50_000) & (scores["train_conversions"] >= 10)].copy()
    top_train = train_pool.nlargest(min(100, len(train_pool)), "train_index")
    testable = top_train[top_train["impressions_P3"] >= 10_000]
    baseline_test = train_pool[train_pool["impressions_P3"] >= 10_000]
    temporal = {
        "train_period": "2026-08-11至2026-10-05（56天）",
        "test_period": "2026-10-06至2026-11-02（28天）",
        "train_eligible_materials": int(len(train_pool)),
        "top100_with_test_impressions_ge_10000": int(len(testable)),
        "top100_test_index_median": float(testable["test_index_raw"].median()) if len(testable) else None,
        "top100_test_index_ge_100_share": float((testable["test_index_raw"] >= 100).mean()) if len(testable) else None,
        "train_pool_test_index_median": float(baseline_test["test_index_raw"].median()) if len(baseline_test) else None,
        "train_pool_test_index_ge_100_share": float((baseline_test["test_index_raw"] >= 100).mean()) if len(baseline_test) else None,
        "train_test_spearman_all_testable": float(spearmanr(baseline_test["train_index"], baseline_test["test_index_raw"], nan_policy="omit").statistic) if len(baseline_test) > 2 else None,
    }

    sensitivity = {}
    eligible_for_sensitivity = scores[(scores["scope_status"] == "纳入") & (scores["evidence_tier"] != "证据不足")]
    base_top50 = set(eligible_for_sensitivity.nlargest(50, "conservative_index").index)
    for k in [5_000.0, 20_000.0]:
        temp = scores.copy()
        add_eb(temp, k, "_sensitivity")
        top50 = set(temp.loc[eligible_for_sensitivity.index].nlargest(50, "conservative_index_sensitivity").index)
        sensitivity[f"prior_{int(k)}_top50_overlap_with_prior_10000"] = len(base_top50 & top50) / 50

    # Reset URI to a normal column for portable CSV output.
    scores = scores.reset_index().rename(columns={"index": "material_uri"})
    scores = scores.sort_values(["priority_flag", "conservative_index", "conversions"], ascending=[False, False, False])
    scores.to_csv(OUT / "video_scores_all.csv", index=False, encoding="utf-8-sig")

    candidate_columns = [
        "material_uri", "material_id", "title", "category", "duration_bucket", "video_duration",
        "evidence_tier", "recent_evidence", "scored_days", "first_day", "last_day",
        "impressions", "clicks", "conversions", "ctr_weighted", "cvr_weighted", "ipm_raw",
        "baseline_ipm", "eb_ipm", "lcb90_ipm", "eb_index", "conservative_index",
        "impressions_P3", "conversions_P3", "ipm_P3", "recent_ipm_change_vs_P2",
        "conversion_day_rate", "play_3s_rate_weighted", "play_5s_rate_weighted",
        "play_over_rate_weighted", "retention_5s_to_3s", "avg_watch_seconds",
        "people_tags", "material_tags", "product_name", "product_cate", "diagnosis", "video_url",
    ]
    priority = scores[scores["priority_flag"]].sort_values(["conservative_index", "conversions"], ascending=False)
    tests = scores[scores["test_flag"]].sort_values(["eb_index", "conversions"], ascending=False)
    decline = scores[scores["efficiency_decline_flag"] & scores["scope_status"].eq("纳入")].sort_values("recent_ipm_change_vs_P2")
    priority[candidate_columns].to_csv(OUT / "priority_candidates.csv", index=False, encoding="utf-8-sig")
    tests[candidate_columns].to_csv(OUT / "test_candidates.csv", index=False, encoding="utf-8-sig")
    decline[candidate_columns].to_csv(OUT / "efficiency_decline_watchlist.csv", index=False, encoding="utf-8-sig")

    excluded = df[~df["valid_funnel"]].copy()
    excluded[["date", "material_uri", "title", "impressions", "clicks", "conversions", "ctr", "cvr", "pvr", "funnel_identity_error"]].to_csv(
        OUT / "excluded_funnel_anomalies.csv", index=False, encoding="utf-8-sig"
    )
    peer_out = scores.groupby(["peer_group", "category", "duration_bucket"], dropna=False).agg(
        materials=("material_uri", "size"), impressions=("impressions", "sum"), conversions=("conversions", "sum"),
        baseline_ipm=("baseline_ipm", "first"), baseline_source=("baseline_source", "first")
    ).reset_index()
    peer_out.to_csv(OUT / "peer_baselines.csv", index=False, encoding="utf-8-sig")

    quality = {
        "method": "品类×时長同层的 Beta-Binomial 经验贝叶斯代理效率；主排序为90%可信下界指数",
        "financial_roi_available": False,
        "conversion_interpretation": "平台转化事件当量，未验证为支付订单",
        "prior_impressions": PRIOR_IMPRESSIONS,
        "raw_rows": int(len(df)),
        "valid_funnel_rows": int(df["valid_funnel"].sum()),
        "excluded_funnel_rows": int((~df["valid_funnel"]).sum()),
        "excluded_funnel_row_share": float((~df["valid_funnel"]).mean()),
        "invalid_attention_rows": int((~df["valid_attention"]).sum()),
        "materials": int(len(scores)),
        "scope_excluded_materials": int(scores["scope_status"].eq("排除").sum()),
        "scale_evidence_materials": int(scores["evidence_tier"].eq("规模证据").sum()),
        "test_evidence_materials": int(scores["evidence_tier"].eq("验证证据").sum()),
        "priority_candidates": int(len(priority)),
        "test_candidates": int(len(tests)),
        "efficiency_decline_materials": int(len(decline)),
        "global_ipm_after_quality_gate": float(1000 * scores["conversions"].sum() / scores["impressions"].sum()),
        "temporal_validation": temporal,
        "prior_sensitivity": sensitivity,
    }
    (OUT / "scoring_summary.json").write_text(json.dumps(quality, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(quality, ensure_ascii=False, indent=2))
    display_cols = ["material_uri", "title", "category", "impressions", "conversions", "ipm_raw", "eb_index", "conservative_index", "ipm_P3", "recent_ipm_change_vs_P2"]
    print("\nTOP_PRIORITY\n", priority[display_cols].head(30).to_string(index=False))
    print("\nTOP_TEST\n", tests[display_cols].head(15).to_string(index=False))


if __name__ == "__main__":
    main()
