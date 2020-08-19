# https://gist.github.com/davidtsadler/6993747
# Limit: https://developer.ebay.com/support/api-call-limits
# Limit 5,000 API calls per day
from ebaysdk.finding import Connection


# Google API Usage Limits: 100 requests per 100 seconds per user, 500 requests per 100 seconds per project
# https://github.com/burnash/gspread
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

from time import sleep

# Setting for price_search#
AppID = ''
SiteId = ''
ItemLocation = ''
Currency = ''
GetPriceQuantity = 3 #Get only n lower price
# END Setting #


# Item search: price list
# Input: NKV (str)
# Return: {'NKV': ..., 'Price': [... , ... , ...]}
#     or: {'NKV': ..., 'Error': [...]}
def price_search(NKV):

    res_dic = {'NKV': NKV}
    price_list = []
    error_list = []

    try:
        api = Connection(siteid=SiteId, appid=AppID, config_file=None)

        api.execute('findItemsAdvanced', {
            'keywords': NKV,
            'itemFilter': [
                {'name': 'Condition', 'value': 'New'},
                {'name': 'listingType', 'value': 'FixedPrice'}
                # see more in zz_itemResponse.txt
                ],
            'paginationInput': {
                'entriesPerPage': '25', #Get max 25 items information
                'pageNumber': '1'
            },
            'sortOrder': 'CurrentPriceLowest'
        })

        dictstr = api.response.dict()

        i = 1
        for item in dictstr['searchResult']['item']:

            if item['location'] == ItemLocation:

                Price = float(item['sellingStatus']['convertedCurrentPrice']['value'])
                ShippingCost = float(item['shippingInfo']['shippingServiceCost']['value']) 
                #ShippingCurrency = item['shippingInfo']['shippingServiceCost']['_currencyId']     
                #ItemID = item['itemId']
                #Title = item['title']
                #CategoryID = item['primaryCategory']['categoryId']

                #res_dic['Currency_'+str(i)] = ShippingCurrency
                #res_dic['Price_'+str(i)] = Price+ShippingCost
                price_list.append( Price + ShippingCost)

                i += 1

        price_list = sorted(price_list)
        res_dic['Price'] = price_list[:GetPriceQuantity] #Get only GetPriceQuantity lower price, see setting

        return res_dic


#     except ConnectionError as e1:
#         error_list.append(e1)
#         res_dic['Error'] = error_list
#         return res_dic

#     except KeyError as e2:
#         error_list.append(e2)
#         res_dic['Error'] = error_list
#         return res_dic

    except:
        error_list.append('UnknownError')
        res_dic['Error'] = error_list
        return res_dic


def main(start_row, break_after, try_times): #Start row in sheet: Int, Break after check break_after items

    if start_row < 3:
        start_row = 0
    else:
        start_row = start_row - 2

    try:

        SPREADSHEET_KEY = '1svbLlypjnpogJQd4QAzTBirl6MkjqhytGYdoXdS0onQ' # Spreadsheets ID

        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('eBaygetPrices2-e634e5c6eb82.json', scope)
        gc = gspread.authorize(credentials)
        spreadsheet = gc.open_by_key(SPREADSHEET_KEY) #Open Spreadsheet
        sheet_1 = spreadsheet.worksheet("eBay_getPrices_2") # Open sheet by name

        NKV_list = sheet_1.col_values(5) # Get Column 5 "NKW_Code"

        if NKV_list != []:
            del NKV_list[0] #Delete Title

        if NKV_list == []: #Check available NKV_list
        	print('NKV_list = [], Please check.')

        for i in range(start_row , len(NKV_list)):

            if i == start_row + break_after: #test only
                break #test only

            row = i + 2 #Google sheet row
            print('Check NKV: {}, row {} now. Remain {} items'.format(NKV_list[i],row, len(NKV_list) -i ))


            if NKV_list[i] == '': #Check nkv data
                continue
            res_dic = price_search(NKV_list[i]) #Check result

            # Update Lower_Price_1, 2, 3
            if 'Price' in res_dic and res_dic['Price'] != []:
                price_ranges = sheet_1.range(row, 8, row, 8 + len(res_dic['Price']) -1 ) #(Start row, start col, end row, end col)
                
                i = 0
                for cell in price_ranges:
                    cell.value = res_dic['Price'][i]
                    i += 1
                sheet_1.update_cells(price_ranges)

            elif 'Error' in res_dic:
                sheet_1.update_cell(row,12, str(res_dic['Error'])) # Update Error


#     except ConnectionError as e1:
#         print(e1)

    except:
        if len(NKV_list) -i > 1 and try_times < 3:
            try_times += 1
            print('Error in row {}. Try again after 10s'.format(i + 2))
            sleep(10)
            main(row,5000,try_times)
        else:
#             try_times = 0
            print('Error in row {}. Check next row after 10s'.format(i + 2))
            sleep(10)
            main(row+1,5000,0)


# Main
if __name__ == '__main__':
    main(2,5000,0) # (start_row, break_after, try_times)
