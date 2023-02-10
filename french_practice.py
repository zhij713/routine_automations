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
      self.gpt_token = gpt_token #token to hit on chatGPT API
      self.deepl_token = deepl_token #token to hit on deepL API


  def chatGPT_query(self,ask):
    #Inputs a string text, which is asked to ChatGPT through 3rd party Chatbot API
    #Outputs ChatGPT's response
    chatbot = Chatbot({"session_token": self.gpt_token}, conversation_id=None, parent_id=None)
    response = chatbot.ask(ask)['message']
    return response
  
  def deepl_en_to_fr(self,text):
    #Inputs an English string test, which is then translated by DeepL into French
    #Outputs DeepL's French translation
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
    #Inputs a given text and the number of errors associated with it, which will be recorded into the instance's Google Sheet
    #Outputs nothing. Recursively searches for the first empty row in the Google sheet
    if self.ws.find(text): #Case for when the text is already in the sheet and we just need to update the pre-existing error value
      cell = self.ws.find(text)
      self.ws.update_cell(cell.row,cell.col+1,errors)

    else: #Case for when this text is new to the sheet and need to write it to a new row
      cell = self.ws.cell(1+ctr,1) 
      if cell.value is None:
        self.ws.update_cell(1+ctr,1,text)
        self.ws.update_cell(1+ctr,2,errors)
      else:
        return self.write_to_sheets(text,errors,ctr+1)
    
  def prompt_compare(self,prompt):
    #Inputs an English prompt, which I will translate into French. 
    #Then translates the same prompt using DeepL, allowing me to compare my translation vs. the "correct" translation
    #No output. Just records prompt and # of errors to Google Sheet
    print("\nHere is your English prompt:\n",prompt)
    input("\nWrite here:\n")
    print('\n',self.deepl_en_to_fr(prompt))
    num_errors = input("\nPlace number of errors: ")
    self.write_to_sheets(prompt,num_errors)
    
  
  def review(self):
    #No input or output. 
    #Finds previously recorded prompt with the highest # of errors and hits on prompt_compare for another shot at it
    error_scores = [int(i) for i in self.ws.col_values(2)]
    highest = error_scores.index(max(error_scores))
    #print(highest)
    review_prompt = self.ws.cell(1+highest,1).value
    #print(review_prompt)
    self.prompt_compare(review_prompt)



def main():
  gpt_token = '{{GPT_TOKEN}}'
  deepl_auth = '{{DEEPL_TOKEN}}'
  json_credentials = '{{GOOGLE_JSON_TOKEN}}'
  sheet_name = "fren"
  french_ask = "Give me a random short English paragraph that matches B1 level of difficulty" #Asking ChatGPT to give me an English prompt

  practice = Practicer(gpt_token,json_credentials,deepl_auth,sheet_name)

  ask_review = input("Review time? y/n")
  if ask_review == 'y': #If I want to review and retry the prompt with the greatest # of errors
    practice.review()

  prompt = practice.chatGPT_query(french_ask)
  practice.prompt_compare(prompt)



main()
