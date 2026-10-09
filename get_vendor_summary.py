import pandas as pd
import sqlite3
import logging
from ingestion_db import ingest_db

logging.basicConfig(
    filename = "logs/get_vendor_summary.log",
    level = logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode = "a"
)
def create_vendor_summary(conn):
    ''' This will Merge Different Tables into one to get overall summary and we can add new columns in the resulting data'''
    final_table = pd.read_sql("""WITH 
           freightSummary as
           (select vendorNumber,     
                    sum(freight) as Freight_Cost 
                          from vendor_invoice 
                          group by VendorNumber),
                          
                      PurchaseSummary as(select p.VendorNumber,
                      p.VendorName,
                      p.Brand,
                      p.description,
                      p.PurchasePrice,
                      pp.volume,
                      pp.Price as ActualPrice,
                      sum(p.Quantity) as Total_Qt,
                      sum(p.Dollars) As Total_Purchase from purchases p
                      join purchase_prices pp on p.Brand=pp.Brand
                      where p.PurchasePrice>0
                      group by p.VendorName,p.VendorNumber,p.Brand,p.description,p.PurchasePrice
                      order by Total_Purchase),

                      SalesSummary as(select VendorNo,
                      Brand,
                      sum(SalesQuantity) As TotalSalesQt,
                      sum(SalesDollars) as TotalSalesDollar,
                      sum(SalesPrice) As TotalSalesPrice,
                      sum(ExciseTax) As TotalExciseTax
                      from Sales
                      group by VendorNo,Brand)

                      select ps.VendorNumber,
                      ps.VendorName,
                      ps.Brand,
                      ps.description,
                      ps.PurchasePrice,
                      ps.volume,
                      ps.ActualPrice,
                      ps.Total_Qt,
                      ps.Total_Purchase,
                      ss.TotalSalesQt,
                      ss.TotalSalesDollar,
                      ss.TotalSalesPrice,
                      ss.TotalExciseTax,
                      fs.Freight_Cost
                      from PurchaseSummary ps
                      Left join SalesSummary ss 
                      on ps.VendorNumber=ss.VendorNo
                      AND ps.Brand=ss.Brand
                      Left join freightSummary as fs
                      on ps.VendorNumber=fs.VendorNumber
                      order by ps.Total_Purchase DESC""",conn)
    return final_table

def clean_data(df):
    
    # Changing Type from object to float
    df['volume'] = df['volume'].astype('float64')
    
    # Replacing null values with 0
    df.fillna(0,inplace=True)
    
    # Removing whitespaces
    df['VendorName']=df['VendorName'].str.strip()
    df['description']=df['description'].str.strip()

    #Creting New Columns in Table.
    final_table['GrossProfit']=final_table['TotalSalesDollar']-final_table['Total_Purchase']
    final_table['ProfitMargin']=(final_table['GrossProfit']/final_table['TotalSalesDollar']) * 100
    final_table['StockTurnOver']=final_table['TotalSalesQt']/final_table['Total_Qt']
    final_table['SalesToPurchaseRatio']=final_table['TotalSalesDollar']/final_table['Total_Purchase']

    return df

if __name__ == '__main__':
    conn = sqlite3.connect('inventory.db') 

    logging.info("Creating Vendor Summary Table-----------")
    summary_df = create_vendor_summary(conn)
    logging.info(summary_df.head())

    logging.info("Cleaning Data-----------")
    clean_df = clean_data(summary_df)
    logging.info(clean_df.head())

    logging.info("Ingesting Data-----------")
    ingest_db(clean_df,'vendor_sales_summary',conn)
    logging.info("Completed!")
    
