# _*_ coding:gbk _*_
import SMiner as SP
import os
import click

'''Initialize Engine'''
URL='http://www.nhc.gov.cn/cms-search/xxgk/searchList.htm?type=search'

sp1=SP.SuperMiner(url=URL,headless=False)
'''get the full list of objects'''
#Start miner engine
sp1.MineEngine()

#scroll the page to get the full items
SP.Basic_Actions(engine=sp1.engine,Obj_list=sp1.Objects(Id='keyword'),Obj_index=0,send_keys=True,message='接种情况')
#Get properties
attr=SP.Attributes('href',sp1.Objects(Class='wgblist'))
print(sp1.Objects(Class='wgblist'))
print(attr)
#download files
SP.Download(engine=sp1.engine,url_list=attr,data_type='page',file_type='.html')
#Close engine
os.system('pause')
sp1.engine.quit()
#/html/body/div[2]/div[2]/ul


@click.command()
@click.option("--url",help="url you are searching for",default="https://www.bing.com")
@click.option("--NOGUI/--GUI",help="Dsiplay the browser GUI",default=True)
@click.option("--obj",help="The object you want to find. Id,Name,Class,Link,Partial_link,Tag,Xpath,CSS are available for the first parameter",default=("Class","key"),type=(str,str))
@click.option("--scroll",default=10,help="Scroll the page to get more info")
@click.option("--act",help="Actions you want to take action,such as click,enter or other keyboard actions",multiple=True,default="none")
@click.option("--search",help="search the text",type=(str,str,str),default=("Class","key","hello world"))
@click.option("--attr",help="Get the atrributes such as download link of Objects",default="href")
@click.option("--get",help="Download the contents",default=("page",".html","utf-8",True,-1),type=(str,str,str,bool,int))
def  Superminer(url="https://www.bing.com",NOGUI=True,obj=("Class","key"),scroll=10,act="none",get=("page",".html","utf-8",True,-1),attr="href",search=("Class","key","hello world")):
    '''
    Args:
        url:url you are searching for
        NOGUI:Display the browser GUI or not
        obj:The object you want to find. Id,Name,Class,Link,Partial_link,Tag,Xpath,CSS are available for the first parameter
        scroll:the times you want to scroll the page
        act:Actions you want to take,such as:
            click
            r_click
            d_click
        search:search something
        get:Download the contents
    Return:
        0:everything goes well
        -1:error occured
    '''
    #Initialize the engine
    SPE=SP.SuperMiner(url=url,headless=NOGUI,)
    SPE.MineEngine()
    #scroll the page
    if scroll>0:
        SP.Basic_Actions(engine=SPE.engine,Obj_index=-2,send_keys=False,rollpage=True,roll_times=scroll,time_sleep=1)
   #find Objects
    if obj==("Class","key"):
        pass
    else:
        Objs=Find_ele(engine=SPE,keys=obj)
    #actions
    if act=="none":
        pass
    elif act=="click":
        SP.Basic_Actions(engine=SPE.engine,Obj_list=Objs,Obj_index=0,send_keys=False,rollpage=False,click=True)
    elif act=="r_click":
        SP.Basic_Actions(engine=SPE.engine,Obj_list=Objs,Obj_index=0,send_keys=False,rollpage=False,right_click=True)
    elif act=="d_click":
        SP.Basic_Actions(engine=SPE.engine,Obj_list=Objs,Obj_index=0,send_keys=False,rollpage=False,double_click=True)
    
    #search
    if search==("Class","key","Hello world"):
        pass
    else:
        SP.Basic_Actions(engine=SPE.engine,Obj_list=Find_ele(SPE,(search[0],search[1])),Obj_index=0,send_keys=True,rollpage=False,message=search[2])
    #get atrributes
    attrs=SP.Attributes(attr,Objs)
    #download files
    SP.Download(SPE.engine,url_list=attrs,data_type=get[0],file_type=get[1],encode=get[2],web_name=get[3],web_name_index=get[4])
    return 0

def Find_ele(engine,keys):
    if keys[0]=="Class":
        return engine.Objects(Class=keys[1])
    elif keys[0]=="Id":
        return engine.Objects(Id=keys[1])
    elif keys[0]=="name":
        return engine.Objects(Name=keys[1])
    elif keys[0]=="Link":
        return engine.Objects(Link=keys[1])
    elif keys[0]=="P_link":
        return engine.Objects(Partial_link=keys[1])
    elif keys[0]=="Tag":
        return engine.Objects(Tag=keys[1])
    elif keys[0]=="Xpath":
        return engine.Objects(Xpath=keys[1])
    elif keys[0]=="CSS":
        return engine.Objects(CSS=keys[1])
    return -1