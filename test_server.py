from selenium import webdriver
#from selenium.webdriver.firefox.options import Options
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

def abeek_login(id, pwd): # abeek 사이트 접속 후 로그인
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
    #print(driver.current_url)
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
            #print("alert accepted")
            driver.close()
            driver.quit()
            return False, ID_PASSWARD_INCORRECT
        except TimeoutException: # success
            #print("no alert")
            driver_hash[id] = driver
            print(driver_hash)
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
    
    if(id in driver_hash) :
        return True

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    prefs  = {"profile.managed_default_content_settings.images": 2,"profile.default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(executable_path="/usr/local/bin/chromedriver", chrome_options=options)
    driver.get('http://yes.knu.ac.kr/comm/comm/support/main/main.action')
    #print(driver.current_url)
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
            #print("alert accepted")
            driver.close()
            driver.quit()
            return False, ID_PASSWARD_INCORRECT
        except TimeoutException: # success
            #print("no alert")
            driver_hash[id] = driver
            print(driver_hash)
            return True, NO_PROBLEM
    except Exception as e:
        print(e)
        driver.close()
        driver.quit()
        return False, EXCEPTION
    driver.close()
    driver.quit()
    return True, EXCEPTION

def yes_get_personal_info(id):
    if id in driver_hash :
        driver = driver_hash[id]
    else :
        print("현재 로그인 하지 않은 아이디 입니다")
        return []
    
    time.sleep(1)
    driver.execute_script("changeLangage('kor');")
    time.sleep(1)

    driver.execute_script("launchMenu( 'SMAR', '2241', 'stuInfo', '/stud/smar/baseInfo/stuInfo/list.action' );")
    time.sleep(1)

    privacy_dic = {}
    name = driver.find_element_by_css_selector("#stuInfo > table:nth-child(2) > tbody > tr:nth-child(1) > td:nth-child(4)")
    privacy_dic["이름"] = name.text
    stuid = driver.find_element_by_css_selector("#stuInfo > table:nth-child(2) > tbody > tr:nth-child(1) > td:nth-child(2)")
    privacy_dic["학번"] = stuid.text
    grade = driver.find_element_by_css_selector("#stuInfo > table:nth-child(2) > tbody > tr:nth-child(2) > td:nth-child(4)")
    privacy_dic["학년"] = grade.text
    major = driver.find_element_by_css_selector("#stuInfo > table:nth-child(2) > tbody > tr:nth-child(2) > td:nth-child(6)")
    privacy_dic["소속"] = major.text
    phonenumber = driver.find_element_by_css_selector("#stuInfo > table:nth-child(2) > tbody > tr:nth-child(6) > td:nth-child(4)")
    privacy_dic["전화번호"] = phonenumber.text
    email = driver.find_element_by_css_selector("#stuInfo > table:nth-child(2) > tbody > tr:nth-child(6) > td:nth-child(6)")
    privacy_dic["이메일"] = email.text

    print(privacy_dic)
    
    return privacy_dic

def abeek_get_grade_info(id):
    if id in driver_hash :
        driver = driver_hash[id]
    else :
        print("현재 로그인 하지 않은 아이디 입니다")
        return []
    
    print(driver)

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
    #print(grade_dic["completeSubjectList"])

    '''
    driver.execute_script("tab.selectTabPage( 'essentTab' );") # 필수과목 이수내역 클릭

    time.sleep(1)
    
    req = driver.page_source
    soup = BeautifulSoup(req, 'html.parser')
    tr_list = soup.select('#essentPart > div > table > tbody > tr')
    
    subject_list = ["교과목번호","개설학과","교과목명","교과구분","학점","학기","평점"]

    necessary_subject_list = []
    i=0
    j=0
    for tr in tr_list:
        td_list = tr.select("td")
        if i >= 1:
            subject_dic = {}
            for td in td_list:
                subject_dic[subject_list[j]] = td.text
                j+=1
            necessary_subject_list.append(subject_dic)
        j=0
        i+=1
    if len(necessary_subject_list) >= 1:
        del necessary_subject_list[-1]
    grade_dic["requiredSubjectList"] = necessary_subject_list
    #print(grade_dic["필수"])

    driver.execute_script("tab.selectTabPage( 'designTab' );") # 설계과목 이수내역 클릭

    time.sleep(1)

    req = driver.page_source
    soup = BeautifulSoup(req, 'html.parser')
    tr_list = soup.select('#designPart > div > table > tbody > tr')

    design_subject_list = []
    i=0
    j=0

    for tr in tr_list:
        td_list = tr.select("td")
        if i >= 1:
            subject_dic = {}
            for td in td_list:
                subject_dic[subject_list[j]] = td.text
                j+=1
            design_subject_list.append(subject_dic)
        j=0
        i+=1
    if len(design_subject_list) >= 1:
        del design_subject_list[-1]
    grade_dic["designSubjectList"] = design_subject_list
    #print(grade_dic["설계"])
    '''

    '''      
    driver.execute_script("tab.selectTabPage( 'essentTab' );") # 필수과목 이수내역 클릭

    time.sleep(1)

    tr_list = driver.find_elements_by_css_selector('#essentPart > div > table > tbody > tr') # 필수과목 html table

    subject_list = ["교과목번호","개설학과","교과목명","교과구분","학점","학기","평점"]
    
    necessary_subject_list = []
    i=0
    j=0
    for tr in tr_list:
        td_list = tr.find_elements_by_css_selector("td")
        if i >= 1:
            subject_dic = {}
            for td in td_list:
                subject_dic[subject_list[j]] = td.text
                j+=1
            necessary_subject_list.append(subject_dic)
        j=0
        i+=1
    grade_dic["필수"] =  necessary_subject_list
    #print(grade_dic["필수"])
   
    driver.execute_script("tab.selectTabPage( 'designTab' );") # 설계과목 이수내역 클릭

    time.sleep(1)

    tr_list = driver.find_elements_by_css_selector('#designPart > div > table > tbody > tr') # 설계과목 html table

    design_subject_list = []
    i=0
    j=0
    for tr in tr_list:
        td_list = tr.find_elements_by_css_selector("td")
        if i >= 1:
            subject_dic = {}
            for td in td_list:
                subject_dic[subject_list[j]] = td.text
                j+=1
            design_subject_list.append(subject_dic)
        j=0
        i+=1
    grade_dic["설계"] = design_subject_list
    #print(grade_dic["설계"])
    '''
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
                #print(td_list[10].text)
                if td_list[10].text == "승인":
                    get_grade_info_dic["영어성적"] = "pass"
        i+=1
    
    driver = this_scene
    td = driver.find_element_by_css_selector('#gridM1_0 > td.pass_yn')
    
    if td.text == "합격":
        get_grade_info_dic["영어성적"] = "pass"

    #print("영어성적: ", get_grade_info_dic["영어성적"])

    driver = this_scene
    tr_list = driver.find_elements_by_css_selector('#grid42 > div.data > table > tbody > tr')
    i = 0
    sum_filed_trip = 0 # 현장실습 학점 합
    for tr in tr_list:
        if i >= 1:
            td_list = tr.find_elements_by_css_selector("td")
            if(len(td_list) > 1) :
                #print(td_list[3].text)
                sum_filed_trip += int(td_list[3].text)
        i+=1
    
    driver = this_scene
    tr_list = driver.find_elements_by_css_selector('#grid43 > div.data > table > tbody > tr')
    i = 0
    for tr in tr_list:
        if i >= 1:
            td_list = tr.find_elements_by_css_selector("td")
            if(len(td_list) > 1) :
                #print(td_list[3].text)
                sum_filed_trip += float(td_list[3].text)
            
        i+=1
    get_grade_info_dic["현장실습"] = str(int(sum_filed_trip))

    driver = driver_hash[id]
    driver.find_element_by_css_selector('#KEES_2242_stuaFolder > a').click() # Keess>지도교수상담>전체상담내역 화면전환
    driver.find_element_by_css_selector('#KEES_2241_keesStuAdvcAll > a').click()
    time.sleep(1)

    td = driver.find_element_by_css_selector("#wrap > div.contents > div.contents_box > div.contents_body > div.group_table.mb_30 > table > tbody > tr:nth-child(1) > td")

    counsel = td.text[0:-2]
    #print(counsel)
    get_grade_info_dic["공학상담"] = counsel
    
    grade_dic["getGradeInfo"] = get_grade_info_dic

    #print("현장실습: ", get_grade_info_dic["현장실습"])

    # 로그아웃
    if id in driver_hash :
        driver_hash[id].close()
        driver_hash[id].quit()
        del driver_hash[id]        
    else :
        print("현재 로그인 하지 않은 아이디 입니다")

    print("logout")
    print(driver_hash)

    return grade_dic

def yes_get_grade_info(id):
    if id in driver_hash :
        driver = driver_hash[id]
    else :
        print("현재 로그인 하지 않은 아이디 입니다")
        return []
    
    print(driver)

    driver.execute_script("changeLangage('kor');")
    time.sleep(1)
    driver.execute_script("launchMenu( 'SCOR', '2241', 'certRecEnq', '/cour/scor/certRec/certRecEnq/list.action' );")
    time.sleep(1)

    grade_dic = {}
    get_grade_info_dic = {}

    req = driver.page_source
    soup = BeautifulSoup(req, 'html.parser')
    td_list = soup.select("#certRecAcadStatsGrid_0 > td")

    cheongSeong_culture_dic = {}
    cheongSeong_basic_dic = {}
    cheongSeong_core_dic = {}
    cheongSeong_basic_list = ["독서와토론","사고교육","글쓰기","실용영어","소프트웨어"]
    cheongSeong_core_list = ["인문사회", "자연과학"]
    cheongSeong_culture_list = ["첨성인기초 - 독서와토론", "첨성인기초 - 사고교육", "첨성인기초 - 글쓰기", "첨성인기초 - 실용영어",
        "첨성인기초 - 소프트웨어", "첨성인핵심 - 인문사회", "첨성인핵심 - 자연과학", "첨성인일반", "없음", "비고(인문교양)"]
    i = 0
    if(len(td_list) > 0):
        for td in td_list:
            if td.text != '' and i <= 4:
                cheongSeong_basic_dic[cheongSeong_basic_list[i]] = td.text
            if td.text != '' and i <= 6 and i > 4 :
                cheongSeong_core_dic[cheongSeong_core_list[i-5]] = td.text
            if td.text != '' and i > 6 and i != 8:
                cheongSeong_culture_dic[cheongSeong_culture_list[i]] = td.text
            i+=1
    
    cheongSeong_culture_dic["첨성인기초"] = cheongSeong_basic_dic
    cheongSeong_culture_dic["첨성인핵심"] = cheongSeong_core_dic
    grade_dic["첨성인교양"] = cheongSeong_culture_dic
    #print(get_grade_info_dic)
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
    
    if("전공" in get_grade_info_dic) :
        major = int(get_grade_info_dic[grade_list[grade_list.index("전공")]])
    else :
        major = 0
    if "공학전공" in get_grade_info_dic :
        major += int(get_grade_info_dic[grade_list[grade_list.index("공학전공")]])
    get_grade_info_dic["전공"] = str(major)

    if("교양" in get_grade_info_dic) :
        culture = int(get_grade_info_dic[grade_list[grade_list.index("교양")]])
    else :
        culture = 0
    
    if("전공기반" in get_grade_info_dic) :
        culture += int(get_grade_info_dic[grade_list[grade_list.index("전공기반")]])
    if("기본소양" in get_grade_info_dic) :
        culture += int(get_grade_info_dic[grade_list[grade_list.index("기본소양")]])
    get_grade_info_dic["교양"] = str(culture)

    
    get_grade_info_dic["전공"] = str(major)
    driver.execute_script("launchMenu( 'SMAR', '2241', 'stuAdvcAll', '/stud/smar/advcStu/stuAdvcAll/list.action' );") 
    td_list = driver.find_elements_by_css_selector("#content > table > tbody > tr:nth-child(2) > td")
    
    i = 0
    counsel_list = ["상담","공학상담"]
    for td in td_list :
        get_grade_info_dic[counsel_list[i]] = (td.text)[0]
        i += 1

    get_grade_info_dic["상담"] = str(int(get_grade_info_dic["상담"]) + int(get_grade_info_dic["공학상담"]))
    
    #get_grade_info_dic["공학인증"] = str(sum)
    grade_dic["getGradeInfo"] = get_grade_info_dic
    #print(grade_dic)

    # 로그아웃
    if id in driver_hash :
        driver_hash[id].close()
        driver_hash[id].quit()
        del driver_hash[id]        
    else :
        print("현재 로그인 하지 않은 아이디 입니다")

    print("logout")
    print(driver_hash)

    return grade_dic

def handle_client(connectionSock, addr):
    print("connect")
    data = connectionSock.recv(1024)
    inputdic = json.loads(data)
    #print(inputdic)

    req = inputdic['requestType']
    major = inputdic['major']
  
    if (req == "login") and (major == "abeek"): # 심컴이 로그인 요청
        id = inputdic['id']
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
        id = inputdic['id']

        outputdic = abeek_get_grade_info(id)

        jsonstr = json.dumps(outputdic)

        connectionSock.send(jsonstr.encode())
    elif (req == "login") and (major == "global"): # 글솦이 로그인 요청
        id = inputdic['id']
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
        id = inputdic['id']

        outputdic = yes_get_grade_info(id)

        jsonstr = json.dumps(outputdic)

        connectionSock.send(jsonstr.encode())
    elif (req == "getPersonalInfo") :
        id = inputdic['id']

        outputdic = yes_get_personal_info(id)

        jsonstr = json.dumps(outputdic)

        connectionSock.send(jsonstr.encode())

    elif (req == "logout") :
        id = inputdic['id']

        if id in driver_hash :
            driver_hash[id].close()
            driver_hash[id].quit()
            del driver_hash[id]
            outputdic = {"logout":"success"}
        else :
            print("현재 로그인 하지 않은 아이디 입니다")
            outputdic = {"logout":"success"}

        jsonstr = json.dumps(outputdic)
        connectionSock.send(jsonstr.encode()) 
        print("logout")
        print(driver_hash)

    connectionSock.close()

def server():
    print("Starting server... test_server.py")
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.bind(('0.0.0.0', 4567))
    serverSock.listen()
    while True:
        (connectionSock, addr) = serverSock.accept()
        t = threading.Thread(target=handle_client, args=(connectionSock, addr))
        t.daemon = True
        t.start()

server()

