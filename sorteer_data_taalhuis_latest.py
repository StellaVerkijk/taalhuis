"""
Script om uitdraai van de data van de taalhuis website te ordenen in 1 excel file. 
@author StellaVerkijk

Dit script klopte voor de data van 19 januari, het enige wat ik heb veranderd ten opzichte van het script van de data van 18 oktober is dat ik in de main functie een paar regels code heb toegevoegd voor het geval dat prijzen_lesmat korter is dan alles_df omdat de laatste paar entries geen kosten voor lesmaterialen hadden. 
"""

import pandas as pd
from decimal import *
import sys

def read_files(file_lesmaterialen, file_creditcardfees, file_alles):
    """
    :param file_lesmaterialen: str; dir naar .csv file
    :param file_creditcardfees: str; dir naar.csv file
    :param file_alles: str; dir naar .xlsx file, waarbij gegevens gesorteerd zijn in kolommen in excel
    """
    
    lesmat_df = pd.read_csv(file_lesmaterialen, skip_blank_lines=False) #encoding = 'cp1252')
    credit_df = pd.read_csv(file_creditcardfees, skip_blank_lines=False)
    alles_df = pd.read_excel(file_alles)
    
    return(lesmat_df, credit_df, alles_df)

def process_lesmat(alles_df):
    lesmat_list = alles_df['Teaching materials'].tolist()
    
    list_prices = []
    for item in lesmat_list:
        temp_euro_list = []
        if type(item) == float:
            list_prices.append('none')
        else:
            temp_list = item.split('|')
            for entry in temp_list:
                if entry.startswith(' €'):
                    temp_euro_list.append(entry.strip())
            list_prices.append(temp_euro_list)
      
    process_prices = []
    for entry in list_prices:
        if entry == 'none':
            process_prices.append('none')
        if type(entry) == list and len(entry) == 1:
            process_prices.append(entry)
        if type(entry) == list and len(entry) > 1:
            amount1 = entry[0].split('\r')[0].strip()
            amount2 = entry[1].strip()
            process_prices.append([amount1, amount2])
    
    prijzen_lesmat = []
    for item in process_prices:
        if item == 'none':
            prijzen_lesmat.append(0)
        if type(item) == list and len(item) == 1:
            price_euro = item[0]
            price = price_euro[1::]
            p = float(price)
            prijzen_lesmat.append(p)
        if type(item) == list and len(item) > 1:
            price_euro_1 = item[0]
            price_euro_2 = item[1]
            price1 = price_euro_1[1::]
            price2 = price_euro_2[1::]
            p = Decimal(price1) + Decimal(price2)
            prijzen_lesmat.append(float(p))   
    return(prijzen_lesmat)

def process_creditcardfees(credit_df):
    credit_list = credit_df['Creditcard Fee (Price)'].tolist()
    control_list = process_productline(sys.argv[3])
    credit_fees = []
    for item in credit_list:
        if type(item) == str:
            info = item.split(' ')[0]
            price = info.replace(',', '.')
            credit_fees.append(float(price))
        else:
            credit_fees.append(0)

    if len(credit_fees) < len(control_list):
        for i in range(len(control_list) - len(credit_fees)):
            credit_fees.append(0)

    return (credit_fees)

def process_extras(alles_df):
    extras = alles_df['Extras'].tolist()
    extra_fees = []
    for entry in extras:
        if type(entry) == str:
            temp_list = entry.split('|')
            temp_temp_list = temp_list[-1].split('€')
            amount = temp_temp_list[-1]
            amount_new = amount.replace(',', '.')
            extra_fees.append(float(amount_new))
        else:
            extra_fees.append(0)
    return(extra_fees)

def process_productline(file_productline):
    productline_df = pd.read_csv(file_productline, skip_blank_lines=False) #, encoding = 'cp1252')
    list_productline = productline_df['Productline 1'].tolist()
    #new_productline = []
    #for item in list_productline:
    #    splitted = item.split('#')
    #    new_productline.append(splitted[0])
    #return(new_productline)
    return(list_productline)            

def main():
    file1 = sys.argv[1]
    file2 = sys.argv[2]
    file3 = sys.argv[3]
    file4 = sys.argv[4]
    outfile = sys.argv[5]
    lesmat_df, credit_df, alles_df = read_files(file1, file2, file4) #("lesmaterialen_checkout-2021-11-03.csv", "creditcardfee_checkout-2021-11-03.csv", "alles_checkout-2021-11-03.xlsx")
    list_productline = process_productline(file3)
    alles_df['Productline 1'] = list_productline
    alles_df['Teaching materials'] = lesmat_df['Teaching materials']
    prijzen_lesmat = process_lesmat(lesmat_df)
    if len(prijzen_lesmat) < len(alles_df['Teaching materials'].tolist()):
        x = len(alles_df['Teaching materials'].tolist())-len(prijzen_lesmat)
        print(x)
        for i in range(x):
            prijzen_lesmat.append(0)
    alles_df['Price lesmaterialen (euros)'] = prijzen_lesmat
    credit_fees = process_creditcardfees(credit_df)
    alles_df['Creditcard fee (euros)'] = credit_fees
    extra_fees = process_extras(alles_df)
    alles_df['Extra fees (euros)'] = extra_fees
    alles_df.to_excel(outfile, index = False)
    print(alles_df)
    
main()