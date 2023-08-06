from bs4 import BeautifulSoup
import requests
import yaml

def get_request(url):
    response = requests.get(url)
    return response

def get_soup(url):
    response = get_request(url)
    return BeautifulSoup(response.text,'html.parser')

def extract_shareholder(soup):
    summary = []
    trs = soup.find_all('tr')[1:]
    for tr in trs:
        tds = tr.find_all('td')
        d = {
            'index':tds[0].text.strip(),
            'name' : tds[1].text.strip(),
            'volume' : convert_text_to_number(tds[2].text.strip()),
            'percent' : convert_text_to_number(tds[3].text.strip()),
        }
        summary.append(d)
    return summary

def convert_text_to_number(txt):
    try:
        txt = txt.replace(',','')
        output = float(txt)
    except Exception as e:
        output = txt
    finally:
        return output

def convert_to_yaml(data):
    x = yaml.dump(data,allow_unicode=True)
    return x

def get_shareholders(ticker):
    url = f"https://www.set.or.th/set/companyholder.do?symbol={ticker}&ssoPageId=6&language=th&country=TH"
    soup = get_soup(url)
    table = soup.find_all('div',{'class':'table-responsive'})[0]
    data = extract_shareholder(table)
    data = convert_to_yaml(data)
    return data

if __name__ == "__main__":
    x = get_shareholders('tog')
    print(x)