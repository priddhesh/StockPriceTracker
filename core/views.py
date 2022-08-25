from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup 
import requests
import time
import smtplib
import ssl
from string import Template
from html.parser import HTMLParser
    
def home(request):
  if 'email' and 'company' and 'price' in request.GET:
    company_name = request.GET.get('company')
    company_name = company_name.upper().replace(".","").replace(" ","")
    expected_price = float(request.GET.get('price'))
    user_email = request.GET.get('email')
    choice = request.GET.get('choice')
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    session = requests.Session()
    if choice == "nse":
     html_content = session.get("https://money.rediff.com/companies/market-capitalisation/nse").text
    else :
     html_content = session.get("https://money.rediff.com/companies/market-capitalisation").text
    soup = BeautifulSoup(html_content, 'html.parser')
    a=0
    b=0
    c=0
    d=0
    information = []
    accouncement = []
    str = ""
    str1 = ""
    stock_names = soup.find_all('td', class_="")
    k=0
    for stock_name in stock_names :
      k=k+1
      if k%7 == 1:
        name = stock_name.find('a', class_="")
        if name.text.upper().strip().replace(".","").replace(" ","")==company_name : #checks user's company name input with available companies on website
         company = name.text.strip()
         link = stock_name.find('a', href = True)
         link = link['href']  #link for selected company's stock for more details
         html_link= requests.get("http:"+link).text
         soup = BeautifulSoup(html_link,'html.parser')
         high_low = soup.find('span', { "id" : "highlow_nse" }).text 
         previous_close= soup.find('span',{"id" : "PrevClose_nse"}).text #scraps previous close in nse
         high_low_bse = soup.find('span', { "id" : "highlow" }).text #scraps today's high/low in bse
         previous_close_bse = soup.find('span',{"id" : "PrevClose"}).text #scraps previous close in bse
         HL= soup.find('span',{"id" : "FiftyTwoHighlow_nse"}).text #scraps today's 52wk H/L in nse
         HL_bse = soup.find('span', {"id" : "FiftyTwoHighlow"}).text #scraps today's 52wk H/L in bse
         news = soup.find_all('div', class_="")
         check = soup.find('h2', class_="f14 bold").text
         accs = soup.find_all("a", class_="")
         if "Announcements" not in check :
            for new in news :
             if c>=14 and c<=16 : 
               info = new.find('a', {'rel' : 'nofollow'}).text #scraps latest news related to company
               information.append(info)
             c=c+1
            for i in information :
              str += i
              str+="\n"
         else :
            for acc in accs :
             if d==17 or d==19 : 
                accouncement.append(acc.text) #if news are unavailable, latest accouncements in bse are scrapped
             d=d+1 
            for j in accouncement :
              str1 += j
              str1+="\n" 
         a=k+1
         break
        else :
            continue    

    for stock_name in stock_names :
            b=b+1 
            if b==a:
                stock_price = stock_name.text.replace(",","") #scraps current stock price
    if float(stock_price)>= expected_price : #checks whether current stock price exceeds or equals user's input price
    #templates for output display and email
     if choice == "nse":
      if "Announcements" not in check :
       t = Template('''The price of the stock $stock in NSE market is Rs.$stock_price
Previous Close(Rs.) : $previous_close   
Today's High/Low(Rs.) : $high_low     
52wk H/L (Rs.) : $HL  
Realtime news for $stock : 
$str Link : https:$link''')
      else :
       t = Template('''The price of the stock $stock in NSE market is Rs.$stock_price
Previous Close(Rs.) : $previous_close   
Today's High/Low(Rs.) : $high_low     
52wk H/L (Rs.) : $HL  
Link : https:$link''')
     else :
       if "Announcements" not in check :
        t = Template('''The price of the stock $stock in BSE market is Rs.$stock_price
Previous Close(Rs.) : $previous_close_bse 
Today's High/Low(Rs.) : $high_low_bse
52wk H/L (Rs.) : $HL_bse  
Realtime news for $stock : 
$str Link : https:$link''')   
       else :
        t = Template('''The price of the stock $stock in BSE market is Rs.$stock_price
Previous Close(Rs.) : $previous_close_bse  
Today's High/Low(Rs.) : $high_low_bse     
52wk H/L (Rs.) : $HL_bse
BSE Announcements from $stock :
$str1
Link : https:$link''')
     s = t.substitute(stock=company, stock_price=float(stock_price),link = link, high_low = high_low, previous_close=previous_close, high_low_bse= high_low_bse, previous_close_bse=previous_close_bse,HL=HL,HL_bse=HL_bse,str = str,str1=str1)
     e = user_email
  #code for sending email on sender's mail ID given by the user  
     ctx = ssl.create_default_context()
     password = "jriajpwfcznsbhxy" #sender's app password
     sender = "riddheshpatil.jee@gmail.com"   #sender's mail ID
     receiver = e
     message = s
     with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
              server.login(sender, password)
              server.sendmail(sender, receiver, message)
    else :
      home(request)    
  return HttpResponse('''<html><script>window.location.replace('/');</script></html>''')

def simple_function(request):
    context={
      "title" : "Trigger Python logic"
    }
    return render(request,"core/home.html", context)