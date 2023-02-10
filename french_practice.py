#Notes
"""
-Similar to learning retention, I should be recording this into google sheets so I can review.
-Keep track of errors made, but how? Do I just manually count how many errors there are?
  -I think that would be the best way. Using some text comp between DeepL translation and my translation
  runs the risk of having cases where my translation is correct, just different.
-Workflow A would look like this:
  1. Here's your prompt: 3-5 English sentences. I write my translation
  2. Here's the DeepL Translation: Contrast this against deepL writing
  3. Prompt: How many errors do you count?
  4. Record original prompt, and # of associated errors into Google sheets
Somewhere before or after this workflow, I need to add a review stage:
  1. Review time? y/n
  2. I should probably base the review on highest # of errors. So if I had a prompt from 2 weeks ago w/ 7 errors
  and one yesterday with 8, I should only do the one from yesterday. 
  3. Carry out workflow A. Instead of recording original prompt into new row of cells, just rewrite # of errors
"""

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
  gpt_token = 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..Tp2CPgYD_0hlg_Kq.kyp2Q-bPw9oa8ONwAxUURsddMBTLZ_nr7WXM9mY6ZWdlmHiOSoZqHMIXLkR8sjkCPqQUJjfCCHUsfEbbA8N9ve1vU41UBQ6NWLPlxXPvlIPjqdBPUBzwtI4UJQmBI-LjyQ95XNnwX8Mv9VoSN_Qk-G2jvX5RGIakmAUx_-Sm5cG2RD21oGwYUsm6rJ3HrnZoRAUbZ84GI0f7BgeDCpX3c1BKVy5PpiBUmVhNI43wWWLXcnWfCxe8jmB9koOpMpHU7xY1w1D_lis7zNfEQttAwja3tW6N0TMcOqYi6D6PH5sha0QMgnl7pown8062Lj5TYMQF9b3eEI2ZNkAQ_RiXpRJgWwGpwdt5w4Qf3D6pafzumvXplymGLkyHxD6_y0uQN-eYxzSslJNV5akr0k7iec4rkoZJL4eQg4Strs0V5W01VKhmrYoSrQ_R7pjU3k5SGUdj3JwuqKkNtegL1yHvkGyoH_bpPpe_8pjMw294A0dyIFe9pMcOrYjtxyEKnISuBNboyqgSExOl8oIQdfCVaPkh8F1ngKEYnv373iKoLv0Bil_LOqqV_3-dYviJI7OLEcHvVQM9NMx8IFp6eiLuFBiq4FwePqhSdmgGLV63B2b3TETXh_d83fb5ONH_aoCm1XlUP7Bp5-hr2DEha4SPXPkN2nItCJCuEPQvTQuaLTx9jQN2g5K4fSrW2hPrvzaEtLqNHvMP6JfNLKZ_uW58L-xIGSvyhiN-D3akLdA0H0cS-p28U9yYWId0ZSvrF1eNPM8YMDpJTyzAXfiV_Nzu7APSrTqTpkEFr1yKsk0SefxFowrSIv0tC82eRBwGRnxZP9dNLbc7YTtlAJNa04mfPEyQmKqT3cJZ-hYAFyajBMvo6irvnpX_le309_HON9uWVdQuXhZ8W8nEXkryiYmTucRhLEB1EJv09m33cR9qHgTDfsTR1moWiV5R1ITHTCeQD2700E-tBSfDQAMUKmPAeTLoIW_s7KDZgJCGP8r3E1lzbCMMdRCP9rVgPk0Vs-lSYhkrGTXu4Y7qVfvHwXWR4QD6i6T6oo3oyJhtLmqr6ECoq28efiJnIqVyWwPx6UrPBhj0NoUl8-n97gf5VuHYYyXVujSN0X9MlLwSAn-AkDRALcOzMX7i7H8Lne6DBDt5So9Nmcc4uNZDpWu5Y_zdXPtdW66Lk6ETOMwcOMhbQDNySaludr0xMrrsdvMVmJuLzwoQjE7dkmWmEBpjHl4uxaL0vHtdpcl-EyMhRyBzpeuPHXNCnliaT3pu_Q6aSpqNihHvA9Psa2h57Hd-07EX-iTOf8XgP-f7eOzBGrGDyzx1_9XFDjstDeFQPlVUpZsgBGsGyyab5JnnQW1NbX1jwIqmmxYojQXpyen1YsQnEGSK4jQugL2HrNpMVaZUEAv1EAr5kCmBRxx0Y7GlDZtBr5aee9bIf2XC2DqKHBy6lwl_lP721tNYPQAaZoOlWX-io1uvJ5J-xj9d9mQNeCzJOoEzLHM9F-JVqcPab-GOAqi4BlPWGwULwmOZYYOeyaCUiiHb-Enz0ltwpSeN3-Bv9hKG3g3tX5Ea4jCTV12sw8_D2JB4tQQoAIbjsL2ItxneYjzhVsUp_ZftV9hyR5Wf_N1x_Umhnk1mZvsilQoZJFs200C8A-5V7AJh1GccxLhHNTe6A6ZA8mcl90lFvtR0vPwLrgZeizG2hKQQc-OnYKD6T54KKOJ8RattFyoBBS5c59uIfk_L6lVzDJ_Sa8Sq9XiuFOQGoocqK05f0sT_-EeIcKgCE7a31_9YI5TEJs7Up6EThnBlOhgFm7joXhOonaTCdaVe9mKkWugZAeNY-pry8Ls23wE6Co9m4uTRCqc6RKDS6GEB-tJabZQ9LGXIQM_3SizmhLezWQ8Ews7T1WYLeqvsafSZc9padgb2b96_QjBu6dTjZyIfrT5xzNID9ZAlOPDN2QFqJB8Ky6uscGAJsJOJy7gGw3V1WJOy-8OKLVJtH86Q4o5mLTc92fliLeM4dwpU4_WAVTbGDDR--6FysLlTTVTd5lSLRtEXIxyFngE9YyTQNzThIOrSW9E0yFD7KJ4prR5cj9w5A8Qj_fBVyFOE1xHx-ai_7Sxy-sC8DawNn5bFrYmGelcE3JU-fEJaelZCOgjmSUZ2XP-_TuWdqIRp1WFxG3hYjQPxl6Rsib6jTCS8Rnh9EyOEmJVV4bQTDx72im2aydCruoJUzQnY6W5acnRNuI_tFG5GjjrIVW8oi_06RdxpLejzIq5X8tqouuTZtTI6SeQE0MxShgbLONYdDzn0jHVXoAn07pVgZwXZZWndISiNHwe_hpaJDvefjO0yAqut1htXqsvYWzYjY8dp1dR34RmwGgFf9iXNerGAeSTr3XEhzVd1jskgZswh8lmCokiLw75uteStX0UjwhoeAL33QcYGKv7qQY3gPkxCUF0dE98CZKYtvoHZGRdETHnZnQNBtgsVTRe1i-WFWDtW9nZFN5O814Hzx4osNmFz0BosuklPJ6HSbEIntawgOeoetApwvgWomm_kpEur47EhngTULQ.PhREGqwlEYnEcOZDcqbAkQ'
  deepl_auth = '7f818510-ca38-fc04-df15-e8cd74a151cc:fx'
  json_credentials = "wdilt-375003-9e706b96ffb1.json"
  sheet_name = "fren"

  french_ask = "Give me a random short English paragraph that matches B1 level of difficulty"

  dum = Practicer(gpt_token,json_credentials,deepl_auth,sheet_name)

  ask_review = input("Review time? y/n")
  if ask_review == 'y':
    dum.review()

  prompt = dum.chatGPT_query(french_ask)
  dum.prompt_compare(prompt)


main()