import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import date, timedelta

class WDILT:
    def __init__(self, cred=str, sheetName=str):
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(cred, self.scopes) #access the json key you downloaded earlier 
        self.file = gspread.authorize(self.credentials) # authenticate the JSON key with gspread
        self.ws = self.file.open(sheetName).get_worksheet(0) #create variable for WDILT worksheet

    def review(self,scale1=int,scale2=int):
    #Inputs scale settings used to calculate retention intervals
    #Outputs nothing. Prints the learning nuggets corresponding to each review date
        ret_list = []
        ret_entry = date.today() - timedelta(1)
        ret_list.append(str(ret_entry))
        for x in range(2,6): #Calculates the review dates using scalar parameters, appends to list
            if x == 2:
                ret_entry -= timedelta(scale1)
            else:
                ret_entry -= timedelta(scale1)
            scale1 *= scale2
            ret_list.append(str(ret_entry))
        
        for ret_entry in ret_list:
            ret_date = self.ws.find(ret_entry) #Finds where in sheet the review date is located, if available
            if ret_date is not None:
                col_indexer = 0
                while True: #Loop to iterate over the review date's row and print out each nugget for review
                    wdilt_nugget = self.ws.cell(ret_date.row,ret_date.col + col_indexer).value
                    if wdilt_nugget is None:
                        print('\n')
                        break
                    else:
                        print(wdilt_nugget)
                        print('\n')
                        col_indexer +=1

    def nugget_recorder(self):
        #No input
        #No output. Records today's learning nuggets then writes them to WDILT sheet
        date_checker = self.ws.find(str(date.today()))
        if date_checker is not None: #Checks to see if there are already previous entries from today.
            #If yes, search horizontally across col's in its row until the first empty cell is found, and we
            #will start to add new learning nuggets from there
            x = date_checker.row
            col_indexer = 0
            while True: #Loop to find the first empty cell in the row dedicated to today's date
                free_cell = self.ws.cell(x,date_checker.col + col_indexer).value 
                if free_cell is None:
                    break
                else:
                    col_indexer +=1
        else: #Case for when there is no pre-existing row dedicated to today's date
            x = 1
            col_indexer = 1
            while True: #Loop to find the first empty row to dedicate to today's date
                today_cell = self.ws.cell(x,1).value
                if today_cell is None:
                    self.ws.update_cell(x,1,str(date.today()))
                    break
                else:
                    x+=1
        nugget_list = []
        while True: #Loop to record today's nuggets in list
            new_nugget = input("Write your nugget: \n") 
            if new_nugget == "q": #Case to quit out of loop
                break
            else:
                nugget_list.append(new_nugget)
        for nugget in nugget_list: #Writing today's nuggets from list to sheet in respective row
            self.ws.update_cell(x,nugget_list.index(nugget)+1+col_indexer,nugget)
            
def main():
    json_credentials = "wdilt-375003-9e706b96ffb1.json"
    sheet_name = "WDILT"

    wdilt = WDILT(json_credentials,sheet_name)

    askReview = input("Review time?")
    if askReview == 'y':
        s1 = 5 #First scale setting for retention intervals
        s2 = 3 #Second scale setting for retention intervals
        wdilt.review(s1,s2)
        
    wdilt.nugget_recorder()


main()
