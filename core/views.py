from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup 
import requests
import time
import smtplib
import ssl
from string import Template
from html.parser import HTMLParser
from django.template import Context, loader
from django.shortcuts import render, redirect
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import random

# Create your views here.
from .models import *
from .forms import OrderForm, CreateUserForm
from .filters import OrderFilter

def home(request):
  if 'email' and 'company' and 'price' in request.GET:
    user_email = val()
    company_name = request.GET.get('company')
    company_name = company_name.upper().replace(".","").replace(" ","")
    expected_price = float(request.GET.get('price'))
    choice = request.GET.get('choice')
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    if choice == "nse":
     html_content = session.get("https://money.rediff.com/companies/market-capitalisation/nse").text
    else :
     html_content = session.get("https://money.rediff.com/companies/market-capitalisation").text
    soup = BeautifulSoup(html_content, 'html.parser')
    a=0
    b=0
    c=0
    d=0
    f = 1
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
     f= f-1
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
    else :
      home(request)  
  ctx = ssl.create_default_context()
  password = "" #sender's app password
  sender = ""   #sender's mail ID
  receiver = e
  message = s
  with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
          server.login(sender, password)
          server.sendmail(sender, receiver, message)
  return render(request, 'core/second.html')

@login_required(login_url='login')
def simple_function(request):
    context={
      "title" : "Trigger Python logic"
    }
    return render(request,"core/home.html", context)

def register(request):
   form = CreateUserForm()

   if request.method == 'POST':
    form =  CreateUserForm(request.POST)
    if form.is_valid():
     form.save()
     user = form.cleaned_data.get('username')
     ctx = ssl.create_default_context()
     password = "" #sender's app password
     sender = ""   #sender's mail ID
     receiver = request.POST.get('username')
     message = "You have successfully registered"
     with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
          server.login(sender, password)
          server.sendmail(sender, receiver, message)
     
     
     return redirect('/login')
   context = {'form' : form}
   return render(request, 'core/register.html', context)


def loginpage(request):
 if request.method == 'GET':
	    username = request.GET.get('username')
	    password =request.GET.get('password')

	    user = authenticate(request, username=username, password=password)

 if user is not None:
    email =  request.GET.get('username')
    global val 
    def val():
     return email
    login(request, user) 
    return render(request, 'core/home.html')

 context = {}
 return render(request, 'core/login.html', context)

@login_required(login_url='login')
def company_list(request):
  myList = []
  myList2 = []
  session = requests.Session()
  html_contentNSE = session.get("https://money.rediff.com/companies/market-capitalisation/nse").text
  html_contentBSE = session.get("https://money.rediff.com/companies/market-capitalisation").text

  soup = BeautifulSoup(html_contentNSE, 'html.parser')
  list = soup.find('table', class_="dataTable")
  stock_names = list.find('tbody', class_="")
  companies = stock_names.find_all('a', class_="")

  for company in companies:
    name = company.string
    myList.append(name)
   
  soup2 = BeautifulSoup(html_contentBSE, 'html.parser')
  list2 = soup2.find('table', class_="dataTable")
  stock_names2 = list2.find('tbody', class_="")
  companies2 = stock_names2.find_all('a', class_="")

  for company2 in companies2:
    name2 = company2.string
    myList2.append(name2)
  context = { 'myList' :myList, 'myList2': myList2}
  return render(request, 'core/company_list.html', context)

def generateOTP():
  random_id = ' '.join([str(random.randint(0, 999)).zfill(3) for _ in range(2)])
  random_id = random_id.replace(" ","")
  ctx = ssl.create_default_context()
  password = "" #sender's app password
  sender = ""   #sender's mail ID
  receiver = request.POST.get('username')
  otp = template('''OTP to confirm account is $random_id''')
  message = otp.substitute(random_id = random_id)
  with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=ctx) as server:
          server.login(sender, password)
          server.sendmail(sender, receiver, message)
  