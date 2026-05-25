import csv
import random
from datetime import date, timedelta
import math

random.seed(77)

SKUS = {
    "NS-CHIP-001": {"name":"NorthSnack Original Chips 200g","base_demand":1850,"seasonal_amplitude":0.22,"seasonal_peak_week":28,"promo_lift":1.45,"lead_time_weeks":2,"unit_price":3.49,"unit_cost":1.12},
    "NS-BAR-002":  {"name":"NorthSnack Granola Bar 6-pack","base_demand":1240,"seasonal_amplitude":0.18,"seasonal_peak_week":10,"promo_lift":1.38,"lead_time_weeks":3,"unit_price":4.99,"unit_cost":1.85},
    "NS-MIX-003":  {"name":"NorthSnack Trail Mix 300g","base_demand":980,"seasonal_amplitude":0.31,"seasonal_peak_week":35,"promo_lift":1.52,"lead_time_weeks":2,"unit_price":5.99,"unit_cost":2.10},
}

PROMO_WEEKS = {"NS-CHIP-001":[8,22,36,48],"NS-BAR-002":[5,19,33,46],"NS-MIX-003":[12,26,40,50]}
STOCKOUT_WEEKS = {"NS-CHIP-001":[14,15,28,29,30,44,45],"NS-BAR-002":[10,11,19,20,33,34,46],"NS-MIX-003":[12,13,26,27,28,40,41,50,51]}

start_date = date(2023,1,2)
rows = []

for sku_id,sku in SKUS.items():
    forced_stockouts = STOCKOUT_WEEKS[sku_id]
    demand_history = []

    for week_num in range(104):
        week_date = start_date + timedelta(weeks=week_num)
        week_of_year = week_date.isocalendar()[1]

        seasonal = 1 + sku["seasonal_amplitude"]*math.sin(2*math.pi*(week_of_year-sku["seasonal_peak_week"])/52)
        is_promo = week_of_year in PROMO_WEEKS[sku_id]
        noise = random.gauss(1.0,0.10)
        demand = max(300, int(sku["base_demand"]*seasonal*(sku["promo_lift"] if is_promo else 1.0)*noise))
        demand_history.append(demand)

        is_stockout = week_of_year in forced_stockouts
        if is_stockout:
            stockout_severity = random.uniform(0.5,1.0)
            lost_sales = int(demand*stockout_severity)
            actual_sales = demand - lost_sales
        else:
            lost_sales = 0
            actual_sales = demand

        ma4 = int(sum(demand_history[-4:])/min(4,len(demand_history)))

        rows.append({
            "SKU ID":sku_id,
            "SKU Name":sku["name"],
            "Week Start Date":week_date.strftime("%Y-%m-%d"),
            "Week Number":week_of_year,
            "Month":week_date.strftime("%Y-%m"),
            "Year":week_date.year,
            "Actual Demand Units":demand,
            "Actual Sales Units":actual_sales,
            "Lost Sales Units":lost_sales,
            "Stockout":"Yes" if is_stockout else "No",
            "Is Promotion Week":"Yes" if is_promo else "No",
            "Revenue CAD":round(actual_sales*sku["unit_price"],2),
            "Lost Revenue CAD":round(lost_sales*sku["unit_price"],2),
            "Gross Profit CAD":round(actual_sales*(sku["unit_price"]-sku["unit_cost"]),2),
            "4 Week Moving Average":ma4,
            "Unit Price CAD":sku["unit_price"],
            "Unit Cost CAD":sku["unit_cost"],
        })

with open('/home/claude/cpg-supply-chain/sales-data.csv','w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

from collections import defaultdict
summary_data=defaultdict(lambda:{"demand":0,"sales":0,"lost":0,"stockout_wks":0,"rev":0,"lost_rev":0,"profit":0,"total_wks":0})
for r in rows:
    s=r["SKU ID"]
    summary_data[s]["demand"]+=r["Actual Demand Units"]
    summary_data[s]["sales"]+=r["Actual Sales Units"]
    summary_data[s]["lost"]+=r["Lost Sales Units"]
    summary_data[s]["stockout_wks"]+=1 if r["Stockout"]=="Yes" else 0
    summary_data[s]["rev"]+=r["Revenue CAD"]
    summary_data[s]["lost_rev"]+=r["Lost Revenue CAD"]
    summary_data[s]["profit"]+=r["Gross Profit CAD"]
    summary_data[s]["total_wks"]+=1

print("SKU performance:")
sku_rows=[]
for sku_id,d in summary_data.items():
    fr=round(d["sales"]/d["demand"]*100,1)
    sr=round(d["stockout_wks"]/d["total_wks"]*100,1)
    print(f"  {sku_id}: fill rate {fr}%, stockout {sr}% of weeks, lost revenue ${round(d['lost_rev'],0):,}")
    sku_rows.append({"SKU ID":sku_id,"SKU Name":SKUS[sku_id]["name"],"Total Demand":d["demand"],"Total Sales":d["sales"],"Total Lost Sales":d["lost"],"Fill Rate %":fr,"Stockout Weeks":d["stockout_wks"],"Stockout Rate %":sr,"Total Revenue CAD":round(d["rev"],2),"Total Lost Revenue CAD":round(d["lost_rev"],2),"Total Gross Profit CAD":round(d["profit"],2),"Lead Time Weeks":SKUS[sku_id]["lead_time_weeks"]})

with open('/home/claude/cpg-supply-chain/sku-summary.csv','w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=sku_rows[0].keys())
    writer.writeheader()
    writer.writerows(sku_rows)

reorder_rows=[]
for sku_id,sku in SKUS.items():
    avg=sku["base_demand"]; std=avg*0.12; lt=sku["lead_time_weeks"]; z=1.65
    ss=round(z*std*math.sqrt(lt))
    rop=round(avg*lt+ss)
    annual=avg*52; oc=850; hr=0.25; uc=sku["unit_cost"]
    eoq=round(math.sqrt(2*annual*oc/(hr*uc)))
    reorder_rows.append({"SKU ID":sku_id,"SKU Name":sku["name"],"Avg Weekly Demand":avg,"Std Dev":round(std),"Lead Time Weeks":lt,"Service Level":"95%","Recommended Safety Stock":ss,"Recommended Reorder Point":rop,"EOQ Units":eoq,"Annual Ordering Cost CAD":round(annual/eoq*oc,2),"Annual Holding Cost CAD":round(eoq/2*hr*uc,2)})

with open('/home/claude/cpg-supply-chain/reorder-model.csv','w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=reorder_rows[0].keys())
    writer.writeheader()
    writer.writerows(reorder_rows)

total_lost=sum(d["lost_rev"] for d in summary_data.values())
total_rev=sum(d["rev"] for d in summary_data.values())
print(f"\nTotal lost revenue: ${round(total_lost,0):,}")
print(f"Total revenue: ${round(total_rev,0):,}")
print(f"Lost as % of potential: {round(total_lost/(total_rev+total_lost)*100,1)}%")

with open('/home/claude/cpg-supply-chain/analysis-summary.csv','w',newline='') as f:
    writer=csv.writer(f)
    writer.writerows([
        ["Metric","Value","Notes"],
        ["SKUs analysed","3","Chips, Granola Bar, Trail Mix"],
        ["Analysis period","2 years","January 2023 to December 2024"],
        ["Total lost revenue","$"+f"{round(total_lost,0):,}","Due to stockout events across all SKUs"],
        ["Lost revenue as % of potential",f"{round(total_lost/(total_rev+total_lost)*100,1)}%","Opportunity cost of current replenishment policy"],
        ["Highest stockout rate SKU","NS-MIX-003","Trail Mix — highest demand variability (seasonal peak in late summer)"],
        ["Safety stock model","Z-score at 95% service level","Based on demand variability and supplier lead time"],
        ["EOQ model","Economic Order Quantity","Balances ordering cost against holding cost"],
    ])
print("All files written.")
