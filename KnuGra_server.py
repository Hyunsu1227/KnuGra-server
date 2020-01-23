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

def yes_login(id, pwd):
    #options.add_extension("/home/ubuntu/python/Block-image_v1.1.crx")
    #driver = webdriver.Firefox(firefox_options=options, executable_path="/home/ubuntu/driver/geckodriver")
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
            Alert(driver).accept()
            #print("alert accepted")
            driver.close()
            driver.quit()
            return False
        except TimeoutException: # success
            #print("no alert")
            driver_hash[id] = driver
            print(driver_hash)
            return True
    except Exception as e:
        print(e)
        driver.close()
        driver.quit()
        return False
    driver.close()
    driver.quit()
    return True

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

def yes_get_grade_info(id):
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

    this_scene = driver #비교과 활동 화면 

    get_grade_info_dic["영어성적"] = "fail"
    tr_list = driver.find_elements_by_css_selector('#gridM0 > div.data > table > tbody > tr')
    i = 0

    for tr in tr_list:
        if i >= 1:
            td_list = tr.find_elements_by_css_selector("td")
            if(len(td_list) > 1) :
                print(td_list[10].text)
                if td_list[10].text == "승인":
                    get_grade_info_dic["영어성적"] = "pass"
        i+=1
    
    driver = this_scene
    td = driver.find_element_by_css_selector('#gridM1_0 > td.pass_yn')
    
    if td.text == "합격":
        get_grade_info_dic["영어성적"] = "pass"

    print("영어성적: ", get_grade_info_dic["영어성적"])

    driver = this_scene
    tr_list = driver.find_elements_by_css_selector('#grid42 > div.data > table > tbody > tr')
    i = 0
    sum_filed_trip = 0 # 현장실습 학점 합
    for tr in tr_list:
        if i >= 1:
            td_list = tr.find_elements_by_css_selector("td")
            if(len(td_list) > 1) :
                print(td_list[3].text)
                sum_filed_trip += int(td_list[3].text)
        i+=1
    
    driver = this_scene
    tr_list = driver.find_elements_by_css_selector('#grid43 > div.data > table > tbody > tr')
    i = 0
    for tr in tr_list:
        if i >= 1:
            td_list = tr.find_elements_by_css_selector("td")
            if(len(td_list) > 1) :
                print(td_list[3].text)
                sum_filed_trip += float(td_list[3].text)
            
        i+=1
    get_grade_info_dic["현장실습"] = str(sum_filed_trip)

    driver = driver_hash[id]
    driver.find_element_by_css_selector('#KEES_2242_stuaFolder > a').click() # Keess>지도교수상담>전체상담내역 화면전환
    driver.find_element_by_css_selector('#KEES_2241_keesStuAdvcAll > a').click()

    td = driver.find_element_by_css_selector("#wrap > div.contents > div.contents_box > div.contents_body > div.group_table.mb_30 > table > tbody > tr:nth-child(1) > td")
    print(td.text)
    get_grade_info_dic["공학상담"] = td.text

    grade_dic["getGradeInfo"] = get_grade_info_dic

    print("현장실습: ", get_grade_info_dic["현장실습"])

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
    print(inputdic)

    req = inputdic['requestType']
  
    if (req == "login") :
        id = inputdic['id']
        pwd = inputdic['pwd']

        login_on = yes_login(id,pwd)
        if(login_on):
            outputdic = {"login":"success"}
            jsonstr = json.dumps(outputdic)
        else:
            outputdic = {"login":"fail"}
            jsonstr = json.dumps(outputdic)

        connectionSock.send(jsonstr.encode()) 
    elif (req == "getGradeInfo") :
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
    print("Starting server... test.py")
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serverSock.bind(('0.0.0.0', 3456))
    serverSock.listen()
    while True:
        (connectionSock, addr) = serverSock.accept()
        t = threading.Thread(target=handle_client, args=(connectionSock, addr))
        t.daemon = True
        t.start()

server()

