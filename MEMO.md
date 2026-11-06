# Memo: Three changes to lift renewal response

**To:** Founders · **From:** Aditya Singh · **Re:** Renewal campaign analysis (9,134 customer records)

## The short version

Our renewal response rate is **2.7%, not 14.3%**. The higher number came from 1,093 copied records, almost all of them responders. Once the data is clean, three changes stand out: stop the two offers that do not work, spread what agents do well to every channel, and call customers in order of likelihood to respond. Together they could take response to roughly **4%**, which we should prove with a test before rolling out.

## What I found

1. **The headline number was wrong.** 1,093 of 9,134 records (12%) repeat another customer's lifetime value and income to the cent. 99.7% of these copies are responders, which inflated the response rate about 5x. Every KPI below uses the 8,041 unique customers.
2. **Two offers are wasted.** Offer3 (0.4% response) and Offer4 (0%) went to 30% of customers. Offer2 gets 4.8%.
3. **Agents convert best.** Agents get a 3.8% response, 1.8x the web, branch and call-centre channels combined. They handle 36% of customers but win 51% of responders.
4. **We can rank who to call.** A response model puts half of all responders in the top 20% of customers, 2.5x better than calling at random.
5. **Second policies matter.** Customers with 2 policies have a median lifetime value 4.1x that of single-policy customers, and 35% of customers hold only one.

## What I recommend

| # | Action | Owner | How we will know |
|---|---|---|---|
| 1 | Deduplicate customer records before any campaign report | Ops | Response rate reported on unique customers only |
| 2 | Replace Offer3 and Offer4 with Offer2 for half of those customers; keep the other half as a control | Growth | Response rate, test vs control, after one cycle |
| 3 | Record agent calls that convert and turn them into call, email and web scripts | Sales | Non-agent response rate moving toward 3.8% |
| 4 | Work the renewal list by model score, highest first | Sales | Responders per 100 calls |
| 5 | Offer a second policy to single-policy customers with high scores | Growth | Second-policy rate |

## Risks and what I don't know

- Offers and channels were not assigned at random, so the gaps are associations. The test in action 2 is how we find out whether swapping offers causes the lift.
- The data is IBM's public sample and may be partly simulated, so the method is the point; the numbers need checking on our own book.

*Full analysis, code and data: [README](README.md).*
