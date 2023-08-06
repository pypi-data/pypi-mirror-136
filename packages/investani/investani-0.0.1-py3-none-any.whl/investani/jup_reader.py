# general
# pip install PyYAML
import yaml
import datetime
from dateutil.relativedelta import relativedelta
import json
import os

# data analysis
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from IPython.display import Image,display, Markdown, Latex

# ====================================== Functions ======================================
def get_compound_annual_growth_rate(start_value,end_value,n_year_hold):
    # https://www.investopedia.com/terms/c/cagr.asp
    CAGR = (end_value/start_value)**(1/n_year_hold)-1
    msg = f"You have CAGR = {100*CAGR} % per year"
    print(msg)
    return CAGR

def get_future_value(start_value,compound_rate,n_year_hold):
    # https://www.investopedia.com/terms/f/futurevalue.asp
    multiplier = (1+compound_rate) ** n_year_hold
    FV = start_value * multiplier
    msg = f"if you invested {start_value} with compound rate {100*compound_rate}% for {n_year_hold} years, you will have {FV} as result"
    print(msg)
    return FV

def predict_nextyear_growth_percent(array_of_value):
    # array_of_value: numpy array with 1 dimension
    shape = array_of_value.shape[0]
    years = np.arange(shape).reshape(-1,1)
    regr = RandomForestRegressor(max_depth=2, random_state=0)
    regr.fit(years, array_of_value)
    return regr.predict(np.array(shape).reshape(-1,1))

def calc_growth_percent(list_of_value):
    # make sure that the list of value is orderd from oldest(left) to newest(right)
    # ref: https://stackoverflow.com/questions/53067695/finding-percentage-change-with-numpy#comment102435598_53067895
    a = np.array(list_of_value)
    return np.diff(a) / a[:-1]

def print_dict(a_dict):
    print(json.dumps(a_dict,indent=4, ensure_ascii=False).encode('utf8').decode())

def get_markdown_header(txt,h_lvl=1):
    h_txt = '#' * h_lvl
    return f'{h_txt} {txt}'

def get_markdown_bullet(txt):
    return f'- {txt}'

def get_markdown_img(image_filepath):
    return f"![alt text]({image_filepath} \"hover message\")"

def list_all_files(mypath,with_index=False):
    files = []
    for (dirpath, dirnames, filenames) in os.walk(mypath):
        for f in filenames:
            fp = os.path.join(dirpath,f)
            files.append(fp)
    # sort
    files.sort()
    if with_index:
        output = []
        for index,filename in enumerate(files):
            txt = f"img{index:03d} : {filename}"
            output.append(txt)
        return output
    else:
        return files

def get_markdown_bullets(txt_list:list):
    txt = ''
    for t in txt_list:
        t_ = f'{get_markdown_bullet(t)}\n'
        txt += t_
    return txt

def get_age(date_txt:str):
    dob = datetime.datetime.strptime(date_txt,'%Y-%m-%d')
    today = datetime.datetime.today()
    return relativedelta(today, dob).years

def read_yaml_file(filepath):
    with open(filepath, 'r',encoding='utf-8') as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exception:
            print(exception)
            data = None
        else:
            return data

# ====================================== Specific functions for each sections ======================================
def get_markdown_general_info(data):
    header = get_markdown_header("General info")
    body = ''
    for k,v in data.items():
        body += f"**{k}**: {v}  \n"
    output = header + '\n' + body
    return output

def get_markdown_links(data):
    header = get_markdown_header("Link references")
    body = ''
    for k,v in data.items():
        if k.lower() == 'phone':
            txt = f"**{k}**: {v}  \n"
        else:
            txt = f"**{k}**: [Link]({v})  \n"
        body += txt
    output = header + '\n' + body
    return output

def get_markdown_investment_theme(data):
    header = get_markdown_header("Investment theme")
    body = ''
    for k,v in data.items():
        _result = v['result']
        if _result:
            _result = """<span style="color:green"> Yes </span>
            """
        else:
            _result = """<span style="color:red"> No </span>
            """
        _comment = v['comment']
        txt = f"**{k}**: {_result}, {_comment}  \n"
        body += txt
    output = header + '\n' + body
    return output

def get_markdown_pestel(data):
    header = get_markdown_header("PESTEL")
    body = ''
    for k,v in data.items():
        _result = v['result']
        if _result == True:
            _result = """<span style="color:green"> Yes </span>
            """
        elif _result == False:
            _result = """<span style="color:red"> No </span>
            """
        else:
            _result = """<span style="color:gray"> Natural </span>
            """
        _comment = v['comment']
        txt = f"**{k}**: {_result}, {_comment}  \n"
        body += txt
    output = header + '\n' + body
    return output

def get_markdown_tech_company_checklist(data):
    header = get_markdown_header("Technology company checklist")
    body = ''
    for k,v in data.items():
        _result = v['result']
        if _result == True:
            _result = """<span style="color:green"> Yes </span>
            """
        elif _result == False:
            _result = """<span style="color:red"> No </span>
            """
        else:
            _result = """<span style="color:gray"> Natural </span>
            """
        _comment = v['comment']
        txt = f"**{k}**: {_result}, {_comment}  \n"
        body += txt
    output = header + '\n' + body
    return output

def get_markdown_business_model_canvas(data):
    header = get_markdown_header("Business Model Canvas + Risk evaluation")
    body = ''
    for k,v in data.items():
        txt = f"**{k}**: {v}  \n"
        body += txt
    output = header + '\n' + body
    return output

def get_markdown_analysis(data):
    images = []
    images.append(Markdown('# Business analysis'))
    for k,v in data.items():
        images.append(Markdown(v['comment']))
        images.append(Image(v['image_path']))
    # unpack and show image
    return display(*images)

def get_markdown_5forces(data):
    header = get_markdown_header("5 Forces model")
    body = ''
    for k,v in data.items():
        if k in ['การแข่งขันภายในอุตสาหกรรม','การเข้ามาของคู่แข่งรายใหม่']:
            internal = v['จากต่างชาติ']
            external = v['ในประเทศ']
            txt = f"**{k}**:  \n" + f"- [จากต่างชาติ]: {internal}  \n" + f"- [ในประเทศ]: {external}  \n\n"
        else:
            txt = f"**{k}**: {v}  \n\n"
        body += txt
    output = header + '\n' + body
    return output

def get_markdown_dca(data):
    header = get_markdown_header("Durable competitive advantage[DCA]")
    body = ''
    for k,v in data.items():
        txt = f"**{k}**: {v}  \n\n"
        body += txt
    output = header + '\n' + body
    return output

def get_markdown_swot(data):
    header = get_markdown_header("SWOT analysis")
    body = ''
    for k,v in data.items():
        txt = f"**{k}**: {v}  \n\n"
        body += txt
    output = header + '\n' + body
    return output

def get_markdown_blc_bcg(data):
    contents = []
    contents.append(Markdown('# BLC(business life cycle) and BCG model'))

    for k,v in data.items():
        contents.append(Markdown(f"**{k}**: {v}"))
    
    contents.append(Image('./img/mandatory/bcg_model.png'))
    contents.append(Image('./img/mandatory/business_life_cycle.png'))
    # unpack and show image
    return display(*contents)

def get_markdown_company_presentations(data):
    header = get_markdown_header("Company presentations")
    body = ''
    _tmp_data = []
    for k,v in data.items():
        _tmp_data.append(v)
    
    # sort
    _df = pd.DataFrame(_tmp_data)
    _df.sort_values(by=['issue_date'],ascending=[False],inplace=True)

    # prepare markdown by looping through each row
    for index,row in _df.iterrows():
        markdown_media = get_markdown_media(row['link'],row['title'])
        title = row['title']
        issue_date = row['issue_date']
        bullets = get_markdown_bullets(row['comment'])
        txt = f"""{markdown_media}  \n{title}  \nissue_date: {issue_date}  \n{bullets}
        """
        body += txt.strip()
        body += '\n\n'
    # output
    output = header + '\n' + body + '\n'
    return output

def get_markdown_news(data):
    header = get_markdown_header("News")
    body = ''
    _tmp_data = []
    for k,v in data.items():
        _tmp_data.append(v)
    
    # sort
    _df = pd.DataFrame(_tmp_data)
    _df.sort_values(by=['issue_date'],ascending=[False],inplace=True)

    # prepare markdown by looping through each row
    for index,row in _df.iterrows():
        markdown_media = get_markdown_media(row['link'],row['title'])
        title = row['title']
        issue_date = row['issue_date']
        bullets = get_markdown_bullets(row['comment'])
        txt = f"""{markdown_media}  \n{title}  \nissue_date: {issue_date}  \n{bullets}
        """
        body += txt.strip()
        body += '\n\n'
    # output
    output = header + '\n' + body + '\n'
    return output

def get_markdown_ceo(data):
    contents = []
    contents.append(Markdown('# CEO'))

    for k,v in data.items():
        if k == 'image':
            contents.append(Image(v))
        elif k == 'birth_year':
            age = datetime.date.today().year - v
            contents.append(Markdown(f"**age**: {age}"))
        elif k in ['other_positions','bad_news','comments']:
            txt = f"**{k}**  \n{get_markdown_bullets(v)}"
            contents.append(Markdown(txt))
        else:
            txt = f"**{k}**: {v}"
            contents.append(Markdown(txt))
    # url bad news
    url = 'https://www.google.com/search?q=%E0%B8%98%E0%B8%A3%E0%B8%93%E0%B9%8C+%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%88%E0%B8%B1%E0%B8%81%E0%B8%A9%E0%B9%8C%E0%B8%98%E0%B8%A3%E0%B8%A3%E0%B8%A1+%E0%B9%82%E0%B8%81%E0%B8%87&oq=%E0%B8%98%E0%B8%A3%E0%B8%93%E0%B9%8C+%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%88%E0%B8%B1%E0%B8%81%E0%B8%A9%E0%B9%8C%E0%B8%98%E0%B8%A3%E0%B8%A3%E0%B8%A1+&aqs=chrome.0.69i59j0i19j69i57.1742j0j4&sourceid=chrome&ie=UTF-8'
    md = f"[ตัวอย่าง URL ตรวจสอบข่าวการโกง]({url})"
    contents.append(Markdown(md))
    return display(*contents)

def get_markdown_capital_increase(data):
    header = get_markdown_header("Capital increase")
    body = ''
    for k,v in data.items():
        _detail = v['detail']
        if _detail is not None:
            txt = f"{k}: {v['volume']}, {v['reason']}, {v['issue_date']}, {v['detail']}"
            body += txt
            body += '  \n'
    # if never raise capital
    if body == '':
        body = "**No records**"
    # output
    output = header + '\n' + body + '\n'
    return output

def get_markdown_shareholder(data):
    header = get_markdown_header("Share holders")
    body = ''
    # loop over years/record time
    for k,v in data.items():
        year_quarter = k
        df = pd.DataFrame(v)
        df = df[['name','percent']]
        total_percent = df['percent'].sum()
        body = body + f"### {year_quarter}: toal major holders = {total_percent:.2f}  \n" + df.to_markdown() + ' \n\n'
    output = header + '\n' + body + '\n'
    return output

def get_markdown_financial(data):
    contents = []
    contents.append(Markdown('# Financial'))

    for k,v in data.items():
        txt = f"### {k}"
        contents.append(Markdown(txt))

        for k2,v2 in v.items():
            contents.append(Markdown(f"**{k2}**"))
            txt = f"{get_markdown_bullets(v2)}"
            contents.append(Markdown(txt))
    return display(*contents)

def get_markdown_growth(data):
    contents = []
    contents.append(Markdown('# Growth potential'))

    for k,v in data.items():
        txt = f"### {k}"
        contents.append(Markdown(txt))

        for k2,v2 in v.items():
            if '1' in v2[:10]:
                v2 = add_color(v2,'green')
            contents.append(Markdown(f"- **{k2}**: {v2}"))
    return display(*contents)

def get_markdown_valuation(data):
    contents = []
    contents.append(Markdown('# Valuation'))

    for k,v in data.items():
        contents.append(Markdown(f"**{k}**: {v}"))
    
    # calculation
    contents.append(Markdown(f"-------"))
    calc_current_eps = data['net_profit_lastyear_million'] * 1_000_000 / data['number_of_shares']
    contents.append(Markdown(f"**calc_current_eps**: {calc_current_eps}"))
    calc_expected_eps = data['net_profit_expected_million'] * 1_000_000 / data['number_of_shares']
    contents.append(Markdown(f"**calc_expected_eps**: {calc_expected_eps}"))
    calc_expected_fairprice = data['fair_pe'] * calc_expected_eps
    contents.append(Markdown(f"**calc_fairprice**: {calc_expected_fairprice}"))
    calc_upside = calc_expected_fairprice / data['current_price'] - 1
    txt = f"**calc_upside**: {calc_upside*100} %"
    if calc_upside > 0.08:
        txt = add_color(txt,'green')
    contents.append(Markdown(txt))
    # margin of safety
    margin_of_safety = 0.2
    calc_expected_fairprice_safety = calc_expected_fairprice * (1-margin_of_safety)
    contents.append(Markdown(f"**calc_fairprice_20% margin of safety**: {calc_expected_fairprice_safety}"))
    # TODO[2021-06-21 17:17]: Add 2 * growth rate as PE then multiply with EPS
    return display(*contents)

def get_youtube_link_part(link:str):
    """
    https://www.youtube.com/watch?v=Zcxun9oiUpE
    """
    _link = link
    if 'youtube.com' in _link:
        output = _link.replace("https://www.youtube.com/watch?v=","")
    else:
        output = None
    return output

def get_markdown_media(link,title=None):
    # if it is youtube link, format it
    link_part = get_youtube_link_part(link)
    if link_part is not None:
        output = f"""[![alt text](https://img.youtube.com/vi/{link_part}/0.jpg)](https://www.youtube.com/watch?v={link_part} "hover text")
        """.strip()
    else:
        output = f"[{title}]({link})"
    return output

def add_color(text,color):
    formatted_text = f"<span style=\"color:{color}\"> {text} </span>"
    return formatted_text

if __name__ == "__main__":
    # test functions
    cagr_5year = get_compound_annual_growth_rate(0.64,1.13,5)
    cagr_3year = get_compound_annual_growth_rate(0.37,1.13,3)
    cagr_avg = (cagr_5year+cagr_3year)/2

    print(get_compound_annual_growth_rate(1800000,2850000,5))
    print(get_future_value(1800000,0.09626,5))

    revenue = [20093.18,22127.87,20392.14,23850.89]
    revenue_growth = calc_growth_percent(revenue)
    print(revenue_growth)

    sample_revenue_growth = np.array([0.07754633, 0.07621451, 0.13114635])
    x = predict_nextyear_growth_percent(sample_revenue_growth)
    print(x)

    data = {
        'fair_pe': 25,
        'number_of_shares': 474318000,
        'net_profit_lastyear_million': 68.78,
        'net_profit_expected_million': 140.0,
        'current_price': 6.75
    }
    print(get_markdown_valuation(data))
