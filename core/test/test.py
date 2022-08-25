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
    USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    session = requests.Session()
    html_content = session.get("https://money.rediff.com/companies/Adani-Green-Energy-Ltd/15130762").text
    soup = BeautifulSoup(html_content, 'html.parser')
    high_low = soup.find('span', { "id" : "highlow_nse" }).text 
    print(high_low)
  return render(request, 'core/home.html')