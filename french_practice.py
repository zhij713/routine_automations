from revChatGPT.ChatGPT import Chatbot
import time
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

class Practicer:
  def __init__(self, gpt_token, google_token, deepl_token, sheetName):
      self.scopes = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']
      self.credentials = ServiceAccountCredentials.from_json_keyfile_name(google_token, self.scopes) #access the json key you downloaded earlier 
      self.file = gspread.authorize(self.credentials) # authenticate the JSON key with gspread
      self.ws = self.file.open(sheetName).get_worksheet(0) #create variable for worksheet
      self.gpt_token = gpt_token
      self.deepl_token = deepl_token


  def chatGPT_query(self,ask):
    chatbot = Chatbot({"session_token": self.gpt_token}, conversation_id=None, parent_id=None)
    response = chatbot.ask(ask)['message']
    return response
  
  def deepl_en_to_fr(self,text):
    result = requests.get(
        "https://api-free.deepl.com/v2/translate", 
      params={ 
        "auth_key": self.deepl_token, 
        "source_lang":"EN",
        "target_lang": "FR", 
        "text": text, 
      },
      )
    return result.json()['translations'][0]['text']
  
  
  def write_to_sheets(self,text,errors,ctr=0):
    if self.ws.find(text):
      cell = self.ws.find(text)
      self.ws.update_cell(cell.row,cell.col+1,errors)
    else:
      cell = self.ws.cell(1+ctr,1)
      if cell.value is None:
        self.ws.update_cell(1+ctr,1,text)
        self.ws.update_cell(1+ctr,2,errors)
      else:
        return self.write_to_sheets(text,errors,ctr+1)
    
  def prompt_compare(self,prompt):
    print("\nHere is your English prompt:\n",prompt)
    input("\nWrite here:\n")
    print('\n',self.deepl_en_to_fr(prompt))
    num_errors = input("\nPlace number of errors: ")
    self.write_to_sheets(prompt,num_errors)
    
  
  def review(self):
    error_scores = [int(i) for i in self.ws.col_values(2) ]
    highest = error_scores.index(max(error_scores))
    #print(highest)
    review_prompt = self.ws.cell(1+highest,1).value
    #print(review_prompt)
    self.prompt_compare(review_prompt)



def main():
  gpt_token = 
  deepl_auth = ''
  json_credentials = " "
  sheet_name = "fren"

  french_ask = "Give me a random short English paragraph that matches B1 level of difficulty"

  dum = Practicer(gpt_token,json_credentials,deepl_auth,sheet_name)

  ask_review = input("Review time? y/n")
  if ask_review == 'y':
    dum.review()

  prompt = dum.chatGPT_query(french_ask)
  dum.prompt_compare(prompt)


main()
