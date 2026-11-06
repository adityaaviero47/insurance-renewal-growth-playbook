"""Charts for README from results/results.json."""
import json, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = json.load(open("results/results.json"))
v = R["validation"]
fig, ax = plt.subplots(2, 2, figsize=(11.5, 7.6))
ax[0, 0].bar(["As delivered", "After removing copies"], [v["response_rate_before_dedup"] * 100, R["overall"]["response_rate"] * 100], color=["#E07A2F", "#0052CC"], width=.5)
for i, val in enumerate([v["response_rate_before_dedup"] * 100, R["overall"]["response_rate"] * 100]): ax[0, 0].text(i, val + .3, f"{val:.1f}%", ha="center")
ax[0, 0].set_ylabel("Renewal offer response rate (%)"); ax[0, 0].set_ylim(0, 17)
ax[0, 0].set_title(f"Data check: {v['near_duplicate_rows']:,} copied records inflated the rate 5x")

ch = R["by_channel"]
ax[0, 1].bar([c["Sales Channel"] for c in ch], [c["rate"] * 100 for c in ch], color=["#0052CC" if c["Sales Channel"] == "Agent" else "#9AA5AD" for c in ch])
for i, c in enumerate(ch): ax[0, 1].text(i, c["rate"] * 100 + .08, f"{c['rate']*100:.1f}%", ha="center")
ax[0, 1].set_ylabel("Response rate (%)"); ax[0, 1].set_ylim(0, 4.6)
ax[0, 1].set_title("Channels: agents get 1.8x the response of the rest")

of = sorted(R["by_offer"], key=lambda r: r["Renew Offer Type"])
ax[1, 0].bar([o["Renew Offer Type"] for o in of], [o["rate"] * 100 for o in of], color=["#E07A2F" if o["rate"] < .01 else "#0052CC" for o in of])
for i, o in enumerate(of): ax[1, 0].text(i, o["rate"] * 100 + .1, f"{o['rate']*100:.1f}%\n({o['customers']:,} sent)", ha="center", fontsize=8)
ax[1, 0].set_ylabel("Response rate (%)"); ax[1, 0].set_ylim(0, 6.5)
ax[1, 0].set_title(f"Offers: {R['offer_waste']['share_of_offers_sent']*100:.0f}% of offers went on two that almost never work")

pol = R["value"]["median_clv_by_policies"]
ks = sorted(pol, key=int)
ax[1, 1].bar(ks, [pol[k] / 1000 for k in ks], color=["#9AA5AD" if k != "2" else "#0052CC" for k in ks])
ax[1, 1].set_xlabel("Number of policies held"); ax[1, 1].set_ylabel("Median lifetime value (USD thousand)")
ax[1, 1].set_title("Cross-sell: a 2nd policy goes with 4.1x the lifetime value")
for a in ax.flat: a.spines[["top", "right"]].set_visible(False)
plt.tight_layout(); plt.savefig("results/summary.png", dpi=150)
