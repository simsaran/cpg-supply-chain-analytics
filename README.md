# cpg-supply-chain-analytics
# The Shelf That Kept Running Out
### Demand Forecasting and Stockout Analysis: NorthSnack Foods

I shop at the same grocery store every week. The same shelf is empty every Tuesday morning. I started wondering whether the people restocking it had the data to predict that or whether they find out the same time I do.

This project builds the analytics system that answers that question.

---

## What this is

A demand forecasting and stockout analysis for three snack SKUs at a fictional Canadian CPG company called NorthSnack Foods. Two years of weekly sales data with real seasonal patterns, promotion lifts, and stockout events. The analysis finds where stockouts concentrate, what they cost in lost revenue, and what a better inventory policy would look like.

---

## Live app

[Launch the Supply Chain Analytics Dashboard](your-streamlit-link-here)

---

## What the data showed

Stockouts are not random. They cluster around promotion weeks and seasonal demand peaks — exactly when inventory buffers are lowest and demand is highest. Trail Mix has the worst stockout pattern at 17.3% of weeks, peaking in late summer when outdoor snack demand spikes. Across all three SKUs the stockouts cost $243,315 in lost revenue over two years — 12.1% of total potential revenue.

| SKU | Stockout Rate | Lost Revenue | Fill Rate |
|-----|--------------|-------------|-----------|
| Original Chips | 13.5% of weeks | $71,915 | 89.8% |
| Granola Bar | 13.5% of weeks | $83,802 | 87.4% |
| Trail Mix | 17.3% of weeks | $87,598 | 86.2% |

The 4-week moving average forecast consistently underestimates demand in promotion weeks and seasonal peaks. The fix is a safety stock model calibrated to actual demand variability and supplier lead time rather than a fixed buffer.

---

## Files in this repo

| File | What it is |
|------|-----------|
| app.py | Streamlit app with four tabs: demand and stockouts, forecast vs actuals, reorder model, lost revenue |
| sales-data.csv | 312 weekly records across 3 SKUs with demand, sales, stockout, promotion, and revenue data |
| sku-summary.csv | Aggregated SKU performance with fill rate, stockout rate, and lost revenue |
| reorder-model.csv | Recommended safety stock, reorder points, and EOQ for each SKU |
| analysis-summary.csv | Headline metrics |
| generate-data.py | Python script that built the dataset |
| requirements.txt | Package dependencies |

---

## Skills demonstrated

Demand forecasting with moving average model. Seasonal demand analysis. Stockout identification and cost quantification. Safety stock calculation using Z-score at 95% service level. Economic Order Quantity modelling. Inventory policy design. CPG supply chain analytics. Python, pandas, plotly, Streamlit.

---

## About this project

Part of a portfolio series built while job searching in Canada after graduating from the University of Waterloo. Targeting supply chain analyst and demand planning roles at PepsiCo, Maple Leaf, McCain, and similar CPG companies across Canada.
