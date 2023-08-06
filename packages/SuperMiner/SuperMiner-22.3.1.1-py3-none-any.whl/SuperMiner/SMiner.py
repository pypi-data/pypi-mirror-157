# _*_ coding:gbk _*_
'''
This is the module made for super web miner which enables everyone to download a large quantity of things from certain website,based on selenium/requests/scrapy

Classes:
    SuperMiner():Used for initialize an miner engine

Functions:
    Attributes():get attribues of objects
    Property():get properties of objects
    Basic_Actions():actions simulate the keboard and mouse
    Download():download files

Detailed references please see https://airscker.github.io/SuperWebMiner/
'''


#import modules
from click.types import BOOL
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import os
import time
import lxml
import requests
from urllib3 import request




#Miner Engine
class SuperMiner():
    engine=0#enigine as a member of class,prepared for any operation using engine out of the class area
    def __init__(self,
                 browser='chrome',
                 headless=False,
                 url='https://www.bing.com'):
        '''
        Parameters:
            browser:chrome
                Only support chrome currently.
            headless:True/False
                Hide or display browser GUI,False defaultly.
            url:Any url you want to mine,https://www.bing.com defaultly.

            content:If your object found is search box, you can set content as input.
        
        Functions:
            MineEngine():Initilize the browser engine
            Objects():Get the objects you want to find

        Properties:
            engine:the miner engine used to mine
        '''
        self.browser=browser
        self.headless=headless
        self.url=url
    def MineEngine(self):
        '''
        Return value:
            -1:Error occured
            Others:Run over
        '''
        #Initialize browser
        web_options=Options()
        if self.headless==True:
            #hide the GUI of browser
            try:
                web_options.add_argument('--headless')
                web_options.add_argument('--disable-gpu')
                web_options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
            except:
                print('Initialization error! Please check your configration and try again. ErrorCode:E_Init001')
                return -1
        #Start browser
        if self.browser=='chrome':
            #start chrome       
            try:
                SuperMiner.engine=webdriver.Chrome(options=web_options)                
                SuperMiner.engine.get(self.url)
                #wait=WebDriverWait(SuperMiner.engine,10)
                SuperMiner.engine.implicitly_wait(30)
                #print(engine.page_source)
                #with open('index'+self.url,'w') as f:
                #    f.write(SuperMiner.engine.page_source)
            except:
                print('Web browser start error! Please check your browser driver. ErrorCode:E_WebS001')
                return -1

        else:
            print('Please specify a web browser! ErrorCode:E_WebS002')
            return -1
        print("\nEngine initialized")
        return 0
    def Objects(self,
                Id='None',
                Name='None',
                Class='None',
                Link='None',
                Partial_link='None',
                Tag='None',
                Xpath='None',
                CSS='None'):
        '''
        Get the objects to be found

        Id,Name,Class,Link,Partial_link,Tag,Xpath,CSS:
            Only one element need to be given,if more than one specified, only find the first element. 
            All elements are 'None' defaultly.
        
        return:the list of the objects found
        '''
        obj={'Oid':Id,'Oname':Name,'Oclass':Class,'Olink':Link,'Oplink':Partial_link,'Otag':Tag,'Oxpath':Xpath,'Ocss':CSS}
        Obj='None'
        Obj_name='None'
        for ele in obj.keys():
            if obj[ele]!='None':
                Obj=obj[ele]
                Obj_name=ele
                break

        #find the specified element
        By_value='None'
        Obj_list=[]
        Attri_list=[]
        if Obj_name=='Oid':
            By_value=By.ID           
        elif Obj_name=='Oname':
            By_value=By.NAME
        elif Obj_name=='Oclass':
            By_value=By.CLASS_NAME            
        elif Obj_name=='Olink':
            By_value=By.LINK
        elif Obj_name=='Oplink':
            By_value=By.PARTIAL_LINK_TEXT
        elif Obj_name=='Otag':
            By_value=By.TAG_NAME
        elif Obj_name=='Oxpath':
            By_value=By.XPATH
        elif Obj_name=='Ocss':
            By_value=By.CSS_SELECTOR
        else:
            print('Please specify an existing element you want to find! ErrorCode:E_EleS001')
            return -1
        try:
            Obj_list=SuperMiner.engine.find_elements(by=By_value,value=Obj)
            #print('\nList of the objects Found:',Obj_list)
            #give us a list of all found objects
        except:
            print('Error occured due to the element,mkae sure your target exists and try again.ErrorCode:E_EleS002')

        #exit engine
        #os.system('pause')
        #SuperMiner.engine.quit()
        print('\n'+str(len(Obj_list))+' Objects found')
        return Obj_list

def Attributes(Attribute,Obj_list): 
    '''
    Get the attribute of the page
    parameters:
        Attribute: the attributes you want to get of the objects in Obj_list
        Obj_list:the list of the objects found

    return:attributes of every object in Obj_list

    '''
    try:
        for i in range(len(Obj_list)):
            Obj_list[i]=Obj_list[i].get_attribute(Attribute)
        #print('\nAttributions of the Objects:',Obj_list)
    except:
        print("Please check your attribute,make sure it's right! ErrorCode:E_ErrA001")
        return []
    print('\nAttributes got')
    return Obj_list

def Property(Obj_list):
    '''
    Get the 2-dimension list of the properties of the objects in the Obj_list
    Properties contained:id,lacation,tag_name,size

    return:the properties_list of the objects in the Obj_list,[] means error
    '''
    Prop=[]
    try:
        for i in range(len(Obj_list)):
            Prop.append([Obj_list[i].text,Obj_list[i].id,Obj_list[i].location,Obj_list[i].tag_name,Obj_list[i].size])
        #print(Prop)
    except:
        print('Property error! ErrorCode:E_Prop001')
        return []
    print('\nProperties got')
    return Prop

def Basic_Actions(engine,
                  Obj_list=[],
                  Obj_index=-1,
                  send_keys=False,
                  click=False,
                  clear=False,
                  submit=False,
                  right_click=False,
                  double_click=False,
                  rollpage=False,
                  roll_times=20,
                  time_sleep=1,
                  message='Hello world!'):
    '''
    parameters:
        Obj_list:the list of the objects you found,[] defaultly
        engine:the engine object of the SuperMiner
        Obj_index:the index of the object in Obj_list which you want to type in message,if -1 specified,all objects will be typed in message
        send_keys:input the parameter message,Ture defaultly.
            available Keyboard actions:
                Keys.BACK_SPACE
                Keys.SPACE
                Keys.TAB
                Keys.ESCAPE
                Keys.ENTER
                ...
                Keys.CONTRL,'a'(Ctrl+A)
                Keys.CONTRL,'c'(Ctrl+C)
                ...
                Keys.F1
                ...
        click:click the object,False defaultly.    
        clear:clear the text inputed,False defaultly.    
        submit:submit message and search,False defaultly.
        message:the message you want to search,'Hello world' defaultly
        right_click:Right click the object
        double_click:Double click the object
        rollpage:roll the page,False defaultly
        roll_times:the times page rolled,works when rollpage is True
        time_sleep:time waited for the load of elements in the page,works when rollpage is True

    Return value:
            -1:Error occured
            Others:Run over
    '''
    if Obj_index==-1:
        try:
            for i in range(len(Obj_list)):
                if send_keys==True:
                    Obj_list[i].send_keys(message)
                if submit==True:
                    Obj_list[i].submit()
                    print('submit outdated! recommand to use massage:Keys.ENTER')
                if clear==True:
                    Obj_list[i].clear()
                if click==True:
                    Obj_list[i].click()
                if right_click==True:
                    ActionChains(engine).context_click(Obj_list[i]).perform()
                if double_click==True:
                    ActionChains(engine).double_click(Obj_list[i]).perform()                
                engine.implicitly_wait(100)
        except:
            print('send_keys error! ErrorCode:E_SenK001')
            return -1
    elif Obj_index>=0:
        try:
            if send_keys==True:
                Obj_list[Obj_index].send_keys(message)
            if submit==True:
                Obj_list[Obj_index].submit()
            if clear==True:
                Obj_list[Obj_index].clear()
            if click==True:
                Obj_list[Obj_index].click()
            if right_click==True:
                ActionChains(engine).context_click(Obj_list[Obj_index]).perform()
            if double_click==True:
                ActionChains(engine).double_click(Obj_list[Obj_index]).perform()
            #if drag_drop==True:
            engine.implicitly_wait(100)
        except:
            print('send_keys error! ErrorCode:E_SenK002')
            return -1
    if rollpage==True:
        for i in range(roll_times):
            engine.execute_script('window.scrollBy(0,200)')
            #engine.implicitly_wait(30)
            print('\nPage rolled '+str(i+1)+' times')
            if i==0:
                time.sleep(3*time_sleep)
            else:
                time.sleep(time_sleep)
    return 0

def Download(engine,url_list,data_type='page',file_type='.html',encode='utf-8',folder_name='downloads',web_name=True,web_name_index=-1):
    '''
    parameters:
        engine:the miner engine
        url_list: the list of the urls
        data_type:the type of the data you want to download:
            text(not prefered, 'page' recommanded)
            img
            page(get the whole page)
        file_type:the type of the file saving data
        encode:encoding format of non-img files
        file_name:specify the file name as you want
        folder_name:the file folder you want to save your files downloaded
        web_name:whether to name the file as the link of web, True defaultly
        wen_name_index:the index of  / in site link, the name is choosed from this / to the end of web link

    Default operations:
        downloaded files will be automatically saved in '\downloads' filefolder,each file will be indexed with number 1,2,3... at the last of its name
    
    Return value:
            -1:Error occured
            Others:Run over
    '''
    download_file=0
    file_name=0
    if not os.path.exists(os.getcwd()[:-4]+folder_name):
        try:
            os.makedirs('./'+folder_name)
        except:
            pass
    if data_type=='text':
        print('\nInstead of "text","page" is recommanded now')
        for i in range(len(url_list)):
            if web_name==True:
                file_name=url_list[i].split('/')[web_name_index]
            else:
                file_name='text'+str(time.time())
            with open(folder_name+'/'+file_name+file_type,'w',encoding='utf-8') as fp:
                #print('\nDownloading from:'+url_list[i])
                #download_file+=1
                #text=requests.get(url_list[i])
                #text.encoding=encode
                #fp.write(text.text)
                #fp.close()
                try:
                    print('\nDownloading from:'+url_list[i])
                    download_file+=1
                    text=requests.get(url_list[i])
                    text.encoding=encode
                    fp.write(text.text)
                    fp.close()
                except:
                    print(url_list[i]+' download fail !')
                    fp.close()
                    continue
    elif data_type=='img':
        for i in range(len(url_list)):
            if web_name==True:
                file_name=url_list[i].split('/')[web_name_index]
            else:
                file_name=str(time.time())
            with open(folder_name+'/'+'img'+file_name+file_type,'wb') as fp:                
                try:                    
                    print('\nDownloading from:'+url_list[i])
                    download_file+=1
                    fp.write(requests.get(url_list[i]).content)
                    fp.close()
                except:
                    print(url_list[i]+' download fail !')
                    fp.close()
                    continue
    if data_type=='page':
        for i in range(len(url_list)):
            if web_name==True:
                file_name=url_list[i].split('/')[web_name_index]
                file_name=file_name.replace('?','.')
                file_name=file_name.replace('>','.')
                file_name=file_name.replace('<','.')
                file_name=file_name.replace(':','.')
                file_name=file_name.replace('|','.')
                file_name=file_name.replace('/','.')
                file_name=file_name.replace('"','.')
                file_name=file_name.replace('*','.')
                file_name=file_name.replace('\\','.')
            else:
                file_name='page'+str(time.time())
            with open(folder_name+'/'+file_name+file_type,'w',encoding='utf-8') as fp:
                print('\nDownloading from:'+url_list[i])
                engine.get(url_list[i])
                engine.implicitly_wait(30)
                download_file+=1
                text=engine.page_source
                #text=requests.get(url_list[i])
                #text.encoding=encode
                fp.write(text)
                fp.close()
                #try:
                #    print('\nDownloading from:'+url_list[i])
                #    engine.get(url_list[i])
                #    engine.implicitly_wait(30)
                #    download_file+=1
                #    text=engine.page_source
                #    #text=requests.get(url_list[i])
                #    #text.encoding=encode
                #    fp.write(text)
                #    fp.close()
                #except:
                #    print(url_list[i]+' download fail !')
                #    fp.close()
                #    continue
    else:
        print('Please select a proper data type!, ErrorCode:E_DaTy001')
        return -1
    print('\n'+str(download_file)+' files downloaded')
    return 0

