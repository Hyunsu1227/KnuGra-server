from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import TimeoutException
import argparse
import json
import socket
import threading
import requests
import time

driver_hash = {}

NO_PROBLEM = 0
ID_PASSWARD_INCORRECT = 1
PASSWORD_CHANGE_DATE_THREE_MONTHS = 2
EXCEPTION = 3

def abeek_login(id, pwd): # abeek login
    if id in driver_hash :
        driver_hash[id].close()
        driver_hash[id].quit()
        del driver_hash[id]

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    prefs  = {"profile.managed_default_content_settings.images": 2,"profile.default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", chrome_options=options)
    driver.get('http://abeek.knu.ac.kr/Keess/comm/support/login/loginForm.action')

    try:
        idForm = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID,'usr_id')))
    except Exception as e:
        print(e)
    idForm.send_keys(id)

    WebDriverWait(driver, 5).until(lambda browser: idForm.get_attribute('value') == id)

    try:
        pwdForm = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'passwd')))
    except Exception as e:
        print(e)
    pwdForm.send_keys(pwd)
    WebDriverWait(driver, 5).until(lambda browser: pwdForm.get_attribute('value') == pwd)
    
    try:
        pwdForm.send_keys(Keys.RETURN)
        try:
            WebDriverWait(driver, 1).until(EC.alert_is_present(),
                                        'Timed out waiting for PA creation ' +
                                        'confirmation popup to appear.')
            print(Alert(driver).text)
            if("PASSWORD 변경일이 3개월이 지났습니다." in Alert(driver).text ) :
                return False, PASSWORD_CHANGE_DATE_THREE_MONTHS

            Alert(driver).accept()
            
            driver.close()
            driver.quit()
            return False, ID_PASSWARD_INCORRECT
        except TimeoutException: # success
            
            driver_hash[id] = driver
            
            return True, NO_PROBLEM
    except Exception as e:
        print(e)
        driver.close()
        driver.quit()
        return False, EXCEPTION
    driver.close()
    driver.quit()
    return True, EXCEPTION

def yes_login(id, pwd): # yes 사이트 접속 후 로그인
    if id in driver_hash :
        driver_hash[id].close()
        driver_hash[id].quit()
        del driver_hash[id]

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    prefs  = {"profile.managed_default_content_settings.images": 2,"profile.default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", chrome_options=options)
    driver.get('http://yes.knu.ac.kr/comm/comm/support/main/main.action')
    
    
    try:
        idForm = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID,'usr_id')))
    except Exception as e:
        print(e)
    idForm.send_keys(id)
    WebDriverWait(driver, 5).until(lambda browser: idForm.get_attribute('value') == id)

    try:
        pwdForm = WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, 'passwd')))
    except Exception as e:
        print(e)
    pwdForm.send_keys(pwd)
    WebDriverWait(driver, 5).until(lambda browser: pwdForm.get_attribute('value') == pwd)
    
    try:
        pwdForm.send_keys(Keys.RETURN)
        try:
            WebDriverWait(driver, 1).until(EC.alert_is_present(),
                                        'Timed out waiting for PA creation ' +
                                        'confirmation popup to appear.')
            
            if("PASSWORD 변경일이 3개월이 지났습니다." in Alert(driver).text ) :
                return False, PASSWORD_CHANGE_DATE_THREE_MONTHS
            Alert(driver).accept()
            
            driver.close()
            driver.quit()
            return False, ID_PASSWARD_INCORRECT
        except TimeoutException: # success
            
            driver_hash[id] = driver
            
            return True, NO_PROBLEM
    except Exception as e:
        print(e)
        driver.close()
        driver.quit()
        return False, EXCEPTION
    driver.close()
    driver.quit()
    return True, EXCEPTION

def abeek_get_grade_info(id):
    if id in driver_hash :
        driver = driver_hash[id]
    else :
        print( "abeek_get_grade_info : " + id + " | 현재 로그인 하지 않은 아이디 입니다")
        return []
    

    driver.find_element_by_css_selector('#KEES_2242_stueFolder > a').click()
    driver.find_element_by_css_selector('#KEES_2241_stueStuRecEnq > a').click()
    time.sleep(1)

    grade_list = ["이수학점","평점","교양","전공기초","기본소양","전공기반","공학전공"]
    get_grade_info_dic = {}
    grade_dic = {}
    
    
    td_list = driver.find_elements_by_css_selector("#wrap > div.contents > div.contents_box > div.contents_body > div.info_table.mb_30 > table > tbody > tr:nth-child(3) > td")
    i = 0
    for td in td_list :
        if i != 3:
            get_grade_info_dic[grade_list[i]] = td.text
        if i == 6:
            break
        i += 1
    
    req = driver.page_source
    soup = BeautifulSoup(req, 'html.parser')
    tr_list = soup.select('#tab_FU > table > tbody > tr')
    
    subject_list = ["교과목번호","개설학과","교과목명","교과구분","학점","학기","평점","재이수"]

    complete_subject_list = []
    i=0
    j=0
    for tr in tr_list:
        td_list = tr.select("td")
        if i >= 1:
            subject_dic = {}
            for td in td_list:
                if not(td.text is None):
                    subject_dic[subject_list[j]] = td.text
                j+=1
            complete_subject_list.append(subject_dic)
        j=0
        i+=1
    if len(complete_subject_list) >= 1:
        del complete_subject_list[-1]
    grade_dic["completeSubjectList"] = complete_subject_list
    

    driver = driver_hash[id]
    driver.find_element_by_css_selector('#KEES_2242_stunFolder > a').click() # Keess>학생수강 및 비교과활동>비교과활동 화면전환
    driver.find_element_by_css_selector('#KEES_2241_stunNonsubjMngt > a').click()
    time.sleep(1)

    this_scene = driver #비교과 활동 화면

    get_grade_info_dic["영어성적"] = "fail"
    tr_list = driver.find_elements_by_css_selector('#gridM0 > div.data > table > tbody > tr')
    i = 0

    for tr in tr_list:
        if i >= 1:
            td_list = tr.find_elements_by_css_selector("td")
            if(len(td_list) > 1) :
                
                if td_list[10].text == "승인":
                    get_grade_info_dic["영어성적"] = "pass"
        i+=1
    
    driver = this_scene
    td = driver.find_element_by_css_selector('#gridM1_0 > td.pass_yn')
    
    if td.text == "합격":
        get_grade_info_dic["영어성적"] = "pass"


    driver = this_scene
    tr_list = driver.find_elements_by_css_selector('#grid42 > div.data > table > tbody > tr')
    i = 0
    sum_filed_trip = 0 # 현장실습 학점 합
    for tr in tr_list:
        if i >= 1:
            td_list = tr.find_elements_by_css_selector("td")
            if(len(td_list) > 1) :
                
                sum_filed_trip += int(td_list[3].text)
        i+=1
    
    driver = this_scene
    tr_list = driver.find_elements_by_css_selector('#grid43 > div.data > table > tbody > tr')
    i = 0
    for tr in tr_list:
        if i >= 1:
            td_list = tr.find_elements_by_css_selector("td")
            if(len(td_list) > 1) :
                
                sum_filed_trip += float(td_list[3].text)
            
        i+=1
    get_grade_info_dic["현장실습"] = str(int(sum_filed_trip))

    driver = driver_hash[id]
    driver.find_element_by_css_selector('#KEES_2242_stuaFolder > a').click() # Keess>지도교수상담>전체상담내역 화면전환
    driver.find_element_by_css_selector('#KEES_2241_keesStuAdvcAll > a').click()
    time.sleep(1)

    td = driver.find_element_by_css_selector("#wrap > div.contents > div.contents_box > div.contents_body > div.group_table.mb_30 > table > tbody > tr:nth-child(1) > td")

    counsel = td.text[0:-2]
    
    get_grade_info_dic["공학상담"] = counsel
    
    grade_dic["getGradeInfo"] = get_grade_info_dic

    # 로그아웃
    if id in driver_hash :
        driver_hash[id].close()
        driver_hash[id].quit()
        del driver_hash[id]
    else :
        print( "abeek_get_grade_info_logout : " + id + " | 현재 로그인 하지 않은 아이디 입니다")

    return grade_dic

def yes_get_grade_info(id):
    if id in driver_hash :
        driver = driver_hash[id]
    else :
        print( "yes_get_grade_info : " + id + " | 현재 로그인 하지 않은 아이디 입니다")
        return []

    driver.execute_script("changeLangage('kor');")
    time.sleep(1)
    driver.execute_script("launchMenu( 'SCOR', '2241', 'certRecEnq', '/cour/scor/certRec/certRecEnq/list.action' );")
    time.sleep(1)

    grade_dic = {}
    get_grade_info_dic = {}

    req = driver.page_source
    soup = BeautifulSoup(req, 'html.parser')
    td_list = soup.select("#certRecAcadStatsGrid_0 > td")

    cheongSeong_basic_sum = 0
    cheongSeong_basic_software = 0
    cheongSeong_basic_english = 0
    cheongSeong_core_human = 0
    cheongSeong_core_nature = 0
    cheongSeong_human = 0

    i = 0
    if(len(td_list) > 0):
        for td in td_list:
            if td.text != '' and i <= 2:
                cheongSeong_basic_sum += int(td.text)
            if td.text != '' and i == 3:
                cheongSeong_basic_english += int(td.text)
            if td.text != '' and i == 4:
                cheongSeong_basic_software += int(td.text)
            if td.text != '' and i == 5:
                cheongSeong_core_human += int(td.text)
            if td.text != '' and i == 6:
                cheongSeong_core_nature += int(td.text)
            if td.text != '' and i == 9:
                cheongSeong_human += int(td.text)
            i+=1

    get_grade_info_dic["첨성인기초"] = cheongSeong_basic_sum
    get_grade_info_dic["첨성인기초-실용영어"] = cheongSeong_basic_english
    get_grade_info_dic["첨성인기초-소프트웨어"] = cheongSeong_basic_software
    get_grade_info_dic["첨성인핵심-인문사회"] = cheongSeong_core_human
    get_grade_info_dic["첨성인핵심-자연과학"] = cheongSeong_core_nature
    get_grade_info_dic["인문교양"] = cheongSeong_human

    tr_list = soup.select('#certRecEnqGrid > div.data > table > tbody > tr')
    
    subject_list = ["학기","교과구분","교과목번호","교과목명","학점","평점","점수"]

    complete_subject_list = []
    i=0
    j=0
    for tr in tr_list:
        td_list = tr.select("td")
        if i >= 1:
            subject_dic = {}
            for td in td_list:
                if not(td.text is None):
                    subject_dic[subject_list[j]] = td.text
                j+=1
            complete_subject_list.append(subject_dic)
        j=0
        i+=1
    
    grade_dic["completeSubjectList"] = complete_subject_list

    grade_list = ["교양","교양필수","전공","전공기초","전공선택","전공필수","복수전공","부전공","연계전공","융합전공","전공심화","기초공통","자유선택","일반선택","교직","선수과목","공학전공","전공기반","기본소양","전문교양","교과교육","이수학점","성적평균","평점평균"]
    
    time.sleep(1)
    tr_list = driver.find_elements_by_css_selector("#certRecStatsGrid > div.data > table > tbody > tr")
    td_list = tr_list[-1].find_elements_by_css_selector("td")
    
    sum =  0
    i = 0
    for td in td_list :
        if i > 0 and td.text != '':
            get_grade_info_dic[grade_list[i - 1]] = td.text
        if  (i >=17 and i <= 20 and td.text != ''):
            sum += int(td.text)
        i += 1
    

# 공학전공을 전공에 포함시키는 로직
    if("전공" in get_grade_info_dic) :
        major = int(get_grade_info_dic["전공"])
    else :
        major = 0
    if "공학전공" in get_grade_info_dic :
        major += int(get_grade_info_dic["공학전공"])

    get_grade_info_dic["전공"] = str(major)


# 전공기반 및 기본소양 교양에 포함시키는 로직
    if("교양" in get_grade_info_dic) :
        culture = int(get_grade_info_dic["교양"])
    else :
        culture = 0
    
    if("전공기반" in get_grade_info_dic) :
        culture += int(get_grade_info_dic["전공기반"])
    if("기본소양" in get_grade_info_dic) :
        culture += int(get_grade_info_dic["기본소양"])

    get_grade_info_dic["교양"] = str(culture)

# 상담 및 공학상담
    driver.execute_script("launchMenu( 'SMAR', '2241', 'stuAdvcAll', '/stud/smar/advcStu/stuAdvcAll/list.action' );")
    td_list = driver.find_elements_by_css_selector("#content > table > tbody > tr:nth-child(2) > td")
    
    i = 0
    counsel_list = ["상담","공학상담"]
    
    get_grade_info_dic["상담"] = '0'
    get_grade_info_dic["공학상담"] = '0'

    for td in td_list :
        get_grade_info_dic[counsel_list[i]] = (td.text)[0]
        i += 1
    
    get_grade_info_dic["상담"] = str(int(get_grade_info_dic["상담"]) + int(get_grade_info_dic["공학상담"]))
    
    grade_dic["getGradeInfo"] = get_grade_info_dic
    
    # 로그아웃
    if id in driver_hash :
        driver_hash[id].close()
        driver_hash[id].quit()
        del driver_hash[id]
    else :
        print( "yes_get_grade_info_logout : " + id + " | 현재 로그인 하지 않은 아이디 입니다")

    return grade_dic

def handle_client(connectionSock, addr):
    data = connectionSock.recv(1024)
    inputdic = json.loads(data)

    req = inputdic['requestType']
    major = inputdic['major']

    id = inputdic['id']
    print( time.asctime(time.gmtime()) + " : " + id + " | " + req + " | " + major)

    if (req == "login") and (major == "abeek"): # 심컴이 로그인 요청
        pwd = inputdic['pwd']

        login_on, errorCode = abeek_login(id,pwd)
        if(login_on):
            outputdic = {"login":"success"}
            jsonstr = json.dumps(outputdic)
        else:
            outputdic = {"login":"fail" , "errorCode":errorCode}
            jsonstr = json.dumps(outputdic)

        connectionSock.send(jsonstr.encode())
    elif (req == "getGradeInfo") and (major == "abeek"): # 심컴이 성적 정보 요청
        outputdic = abeek_get_grade_info(id)

        jsonstr = json.dumps(outputdic)

        connectionSock.send(jsonstr.encode())
    elif (req == "login") and (major == "global"): # 글솦이 로그인 요청
        pwd = inputdic['pwd']

        login_on, errorCode = yes_login(id,pwd)
        if(login_on):
            outputdic = {"login":"success"}
            jsonstr = json.dumps(outputdic)
        else:
            outputdic = {"login":"fail", "errorCode":errorCode}
            jsonstr = json.dumps(outputdic)

        connectionSock.send(jsonstr.encode())
    elif (req == "getGradeInfo") and (major == "global"): # 글솦이 성적 정보 요청

        outputdic = yes_get_grade_info(id)

        jsonstr = json.dumps(outputdic)

        connectionSock.send(jsonstr.encode())
    elif (req == "logout") :

        if id in driver_hash :
            driver_hash[id].close()
            driver_hash[id].quit()
            del driver_hash[id]
            outputdic = {"logout":"success"}
        else :
            print( "logout request : " + id + " | 현재 로그인 하지 않은 아이디 입니다")
            outputdic = {"logout":"success"}

        jsonstr = json.dumps(outputdic)
        connectionSock.send(jsonstr.encode())

    connectionSock.close()

    
def server():
    
    print("Starting server...")
    
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.bind(('0.0.0.0', 4567))
    serverSock.listen()
    while True:
        (connectionSock, addr) = serverSock.accept()
        t = threading.Thread(target=handle_client, args=(connectionSock, addr))
        t.daemon = True
        t.start()

server()
