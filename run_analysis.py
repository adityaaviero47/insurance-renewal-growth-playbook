"""Insurance renewal and growth playbook on IBM's public auto insurance customer sample (9,134 US customers, 2011).
Which sales channel and renewal offer get customers to respond, which customers are worth the most,
and how a response-propensity model can decide who gets which offer.
Reproduces every number in README.md:  python run_analysis.py"""
import json, numpy as np, pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score

R = {}
d = pd.read_csv("data/auto_insurance_customers.csv.gz")
d["y"] = d.Response.eq("Yes")
d["clv"] = d["Customer Lifetime Value"]

# ---------- 1. data checks ----------
R["validation"] = dict(customers=len(d), duplicate_ids=int(d.Customer.duplicated().sum()), missing_values=int(d.isna().sum().sum()),
                       negative_values=int((d.select_dtypes("number") < 0).sum().sum()),
                       zero_income=int((d.Income == 0).sum()), zero_income_unemployed_share=float(d.EmploymentStatus[d.Income == 0].eq("Unemployed").mean()))
# near-duplicates: different customer IDs (often in different states) that repeat another record's lifetime value and income
# to the cent - copies, not distinct customers. Keep one record per cluster for every analysis below.
key = ["Customer Lifetime Value", "Income"]
R["validation"]["near_duplicate_rows"] = int(d.duplicated(key).sum())
R["validation"]["near_duplicate_clusters"] = int((d.groupby(key).size() > 1).sum())
R["validation"]["near_duplicate_share"] = float(d.duplicated(key).mean())
R["validation"]["response_rate_before_dedup"] = float(d.y.mean())
R["validation"]["copies_that_are_responders"] = float(d.y[d.duplicated(key)].mean())
R["validation"]["responders_before_dedup"] = int(d.y.sum())
d = d.drop_duplicates(key).reset_index(drop=True)
R["validation"]["unique_customers"] = len(d)
R["overall"] = dict(response_rate=float(d.y.mean()), responders=int(d.y.sum()), median_clv=float(d.clv.median()),
                    avg_monthly_premium=float(d["Monthly Premium Auto"].mean()))

# ---------- 2. renewal response by sales channel and offer ----------
def rate(col):
    g = d.groupby(col).y.agg(rate="mean", customers="size", responders="sum").sort_values("rate", ascending=False)
    return g.round(4).reset_index().to_dict("records")
R["by_channel"] = rate("Sales Channel"); R["by_offer"] = rate("Renew Offer Type")
R["by_employment"] = rate("EmploymentStatus"); R["by_marital"] = rate("Marital Status"); R["by_location"] = rate("Location Code")
ch = d.groupby("Sales Channel").y.mean()
R["channel_gap"] = dict(agent=float(ch["Agent"]), best_other=float(ch.drop("Agent").max()), worst=float(ch.min()),
                        agent_vs_rest=float(ch["Agent"] / d.y[d["Sales Channel"] != "Agent"].mean()),
                        agent_share_of_customers=float((d["Sales Channel"] == "Agent").mean()),
                        agent_share_of_responders=float(d.y[d["Sales Channel"] == "Agent"].sum() / d.y.sum()))
of = d.groupby("Renew Offer Type").y.agg(["mean", "size", "sum"])
weak = of.index[of["mean"] < 0.01]          # offers that almost never get a response
R["offer_waste"] = dict(weak_offers=list(weak), customers_on_weak_offers=int(of.loc[weak, "size"].sum()),
                        share_of_offers_sent=float(of.loc[weak, "size"].sum() / len(d)), responders_on_weak_offers=int(of.loc[weak, "sum"].sum()),
                        best_offer=str(of["mean"].idxmax()), best_offer_rate=float(of["mean"].max()))
# what-if (association, to be A/B tested): weak-offer customers respond at the best offer's rate
extra = R["offer_waste"]["customers_on_weak_offers"] * R["offer_waste"]["best_offer_rate"] - R["offer_waste"]["responders_on_weak_offers"]
R["offer_waste"]["what_if_extra_responders"] = float(extra)
R["offer_waste"]["what_if_response_rate"] = float((d.y.sum() + extra) / len(d))
R["offer_by_channel"] = pd.crosstab(d["Renew Offer Type"], d["Sales Channel"], values=d.y, aggfunc="mean").round(4).to_dict()

# ---------- 3. customer value and cross-sell ----------
c = d.clv.sort_values(ascending=False)
R["value"] = dict(top20_share_of_clv=float(c.head(int(len(c) * .2)).sum() / c.sum()),
                  median_clv_by_policies={int(k): float(v) for k, v in d.groupby("Number of Policies").clv.median().items()},
                  one_policy_share=float((d["Number of Policies"] == 1).mean()))
m1 = d.clv[d["Number of Policies"] == 1].median(); m2 = d.clv[d["Number of Policies"] == 2].median()
R["value"]["two_vs_one_policy_clv"] = float(m2 / m1)

# ---------- 4. response-propensity model (who to call first, with which offer) ----------
feat = ["State", "Coverage", "Education", "EmploymentStatus", "Gender", "Income", "Location Code", "Marital Status",
        "Monthly Premium Auto", "Months Since Last Claim", "Months Since Policy Inception", "Number of Open Complaints",
        "Number of Policies", "Policy Type", "Policy", "Renew Offer Type", "Sales Channel", "Total Claim Amount", "Vehicle Class", "Vehicle Size"]
X = d[feat].copy(); cats = [c_ for c_ in feat if not pd.api.types.is_numeric_dtype(X[c_])]
for c_ in cats: X[c_] = X[c_].astype("category").cat.codes
y = d.y.astype(int).to_numpy()
mdl = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05, max_leaf_nodes=15, min_samples_leaf=40,
                                     categorical_features=[c_ in cats for c_ in feat], random_state=7)
p = cross_val_predict(mdl, X, y, cv=StratifiedKFold(5, shuffle=True, random_state=7), method="predict_proba")[:, 1]
top = np.argsort(-p)[: int(len(p) * .2)]
R["propensity"] = dict(auc=float(roc_auc_score(y, p)), top20_capture=float(y[top].sum() / y.sum()), top20_response=float(y[top].mean()),
                       lift=float(y[top].mean() / y.mean()), note="5-fold cross-validated; offer type and channel are inputs, so scores reflect the offer each customer got")

# ---------- 5. playbook: best observed offer for each customer segment ----------
seg = d.groupby(["EmploymentStatus", "Renew Offer Type"]).y.agg(rate="mean", n="size").reset_index()
seg = seg[seg.n >= 30]
best = seg.sort_values("rate", ascending=False).groupby("EmploymentStatus").head(1).sort_values("rate", ascending=False)
R["playbook"] = best.round(4).to_dict("records")

with pd.ExcelWriter("results/renewal_playbook.xlsx") as x:
    pd.DataFrame(list(R["validation"].items()), columns=["check", "value"]).to_excel(x, sheet_name="Data checks", index=False)
    for k, sh in [("by_channel", "By channel"), ("by_offer", "By offer"), ("by_employment", "By employment")]:
        pd.DataFrame(R[k]).to_excel(x, sheet_name=sh, index=False)
    pd.crosstab(d["Renew Offer Type"], d["Sales Channel"], values=d.y, aggfunc="mean").to_excel(x, sheet_name="Offer x channel")
    best.to_excel(x, sheet_name="Playbook", index=False)
    d.assign(propensity=p).sort_values("propensity", ascending=False)[["Customer", "Sales Channel", "Renew Offer Type", "EmploymentStatus", "clv", "propensity"]].to_excel(x, sheet_name="Call list", index=False)
json.dump(R, open("results/results.json", "w"), indent=2, default=str)
print(json.dumps(R, indent=2, default=str))
