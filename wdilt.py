import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from datetime import date, timedelta
import time

class WDILT: #What Did I Learn Today: For recording daily learning nuggets and reviewing previous days' learnings for retention
    def __init__(self, cred=str, sheetName=str):
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(cred, self.scopes) #access the json key you downloaded earlier 
        self.file = gspread.authorize(self.credentials) # authenticate the JSON key with gspread
        self.ws = self.file.open(sheetName).get_worksheet(0) #create variable for WDILT worksheet

    def review(self,item,ctr=2):
        #Takes input of a cell containing review date
        #No output. Recursively indexes over and prints each learning nugget from the review date's row on the sheet
            wdilt_nugget = self.ws.cell(item.row,item.col + ctr).value
            if wdilt_nugget is None:
                return
            print(wdilt_nugget+'\n')
            self.ws.update_cell(item.row,2,"")
            time.sleep(10) #Time Buffer to avoid read requests limit
            self.review(item,ctr+1)
    
    def review_find(self, ctr=0):
        #Function that recursively finds which rows correspond to the review dates, calling the review() function to print out the nuggets from each row
        cell = self.ws.cell(1+ctr,1)
        if cell.value is None: #Terminal condition, reaching last recorded row on worksheet
            return
        else:
            if self.ws.cell(cell.row,2).value == 'X':
                print(cell.value)
                self.review(cell)
            self.review_find(ctr+1)

    
    def review_of_the_day(self,scale1=int,scale2=int,date=date.today()):
    #Inputs scalar parameters used to calculate review dates in terms of days back from specified date, which is by default today
    #No output. Determines review dates and prints their learning nuggets for review
        for x in range(1,6): #Up to 5 review dates are considered
            if x == 1:
                ret_entry = date - timedelta(1) #First review date is always from 1 day ago
            elif x == 2:
                ret_entry -= timedelta(scale1) 
                scale1 *= scale2 #Increase retention interval for next review date''
            else:
                ret_entry -= timedelta(scale1)
                scale1 *= scale2 #Increase retention interval for next review date''
            ret_date = self.ws.find(str(ret_entry))
            if ret_date is not None:
                self.ws.update_cell(ret_date.row,ret_date.col+1,"X")

        self.review_find() 
            
    

    def colindexer(self,cell, ctr=2):
        #Inputs cell, ideally for today
        #Recursively indexes over cells within the same row and outputs the first found empty cell
        cell_value = self.ws.cell(cell.row,cell.col + ctr).value 
        if cell_value is None:
            next_cell = self.ws.cell(cell.row,cell.col+ctr)
            return next_cell
        else:
            return self.colindexer(cell,ctr+1)     
    
    def rowindexer(self,cell, ctr=0):
        #Inputs cell, ideally for today
        #Recursively indexes over cells within the same column and outputs the first found empty cell
        cell_value = self.ws.cell(cell.row+ctr,1).value 
        if cell_value is None:
            self.ws.update_cell(cell.row+ctr,1,str(date.today()))
            return self.ws.cell(cell.row+ctr,3)
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

    askReview = input("Review time?  y/n")
    if askReview == 'y':
        s1 = 3 #First scale setting for retention intervals
        s2 = 5 #Second scale setting for retention intervals
        check_for_review_dates = [date.today()] #List of dates we want to do review on. By default just includes today, but will be appended if I missed any previous days 

        askCatchup = input("Miss any previous sesions? y/n")

        if askCatchup == 'y': #Case when I missed previous days of doing wdilt review and need to catch up on them
            while True:
                daysBack = input("How many days back (i.e., yesterday = 1)?")
                if not daysBack: #Case for breaking loop, when there are no more missed catchup dates to input
                    break
                check_for_review_dates.append(date.today() - timedelta(int(daysBack)))

        for item in check_for_review_dates:    
            wdilt.review_of_the_day(s1,s2,item)

        wdilt.review_of_the_day(s1,s2)
        
    wdilt.nugget_recorder()

main()
