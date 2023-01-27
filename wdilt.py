import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import date, timedelta

class WDILT: #What Did I Learn Today: For recording daily learning nuggets and reviewing previous days' learnings for retention
    def __init__(self, cred=str, sheetName=str):
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(cred, self.scopes) #access the json key you downloaded earlier 
        self.file = gspread.authorize(self.credentials) # authenticate the JSON key with gspread
        self.ws = self.file.open(sheetName).get_worksheet(0) #create variable for WDILT worksheet

    def review(self,item,ctr=0):
        #Takes input of a cell containing review date
        #No output. Recursively indexes over and prints each learning nugget from the review date's row on the sheet
            wdilt_nugget = self.ws.cell(item.row,item.col + ctr).value
            if wdilt_nugget is None:
                return
            print(wdilt_nugget+'\n')
            self.review(item,ctr+1)
    
    def review_of_the_day(self,scale1=int,scale2=int):
    #Inputs scalar parameters used to calculate review dates in terms of days back from today
    #No output. Determines review dates and prints their learning nuggets for review
        for x in range(1,6): #Up to 5 review dates are considered
            if x == 1:
                ret_entry = date.today() - timedelta(1) #First review date is always from 1 day ago
            elif x == 2:
                ret_entry -= timedelta(scale1) 
            else:
                ret_entry -= timedelta(scale1)
            ret_date = self.ws.find(str(ret_entry))
            if ret_date is not None:
                self.review(ret_date)

            scale1 *= scale2 #Increase retention interval for next review date''
            
    def colindexer(self,cell, ctr=0):
        #Inputs cell, ideally for today
        #Recursively indexes over cells within the same row and outputs the first found empty cell
        cell_value = self.ws.cell(cell.row,cell.col + ctr).value 
        if cell_value is None:
            next_cell = self.ws.cell(cell.row,cell.col+ctr)
            print(next_cell)
            return next_cell
        else:
            return self.colindexer(cell,ctr+1)     
    
    def rowindexer(self,cell, ctr=0):
        #Inputs cell, ideally for today
        #Recursively indexes over cells within the same column and outputs the first found empty cell
        cell_value = self.ws.cell(cell.row+ctr,1).value 
        if cell_value is None:
            self.ws.update_cell(cell.row+ctr,1,str(date.today()))
            return self.ws.cell(cell.row+ctr,2)
        else:
            return self.rowindexer(cell,ctr+1)

    def nugget_recur(self,cell, ctr=0):
        #Inputs cell, ideally empty cell that takes in today's learning nugget
        #No output. Asks for/records learning nuggets into sheet
        nugget = input("New nugget: ")  #
        if nugget == "q":
            return
            
        self.ws.update_cell(cell.row,cell.col+ctr,nugget)
        self.nugget_recur(cell,ctr+1)

    def nugget_recorder(self):
        #No input
        #No output. Finds next empty cell to record learning nuggets for today
        date_checker = self.ws.find(str(date.today()))
        if date_checker is not None: #Checks to see if there are already previous entries from today.
            next_cell = self.colindexer(date_checker)
        else: #Case for when there is no pre-existing row dedicated to today's date
            next_cell = self.rowindexer(self.ws.cell(1,1))

        self.nugget_recur(next_cell)
        

          
def main():
    json_credentials = "wdilt-375003-9e706b96ffb1.json"
    sheet_name = "WDILT"

    wdilt = WDILT(json_credentials,sheet_name)

    askReview = input("Review time?")
    if askReview == 'y':
        s1 = 5 #First scale setting for retention intervals
        s2 = 3 #Second scale setting for retention intervals
        wdilt.review_of_the_day(s1,s2)
        
    wdilt.nugget_recorder()

main()
