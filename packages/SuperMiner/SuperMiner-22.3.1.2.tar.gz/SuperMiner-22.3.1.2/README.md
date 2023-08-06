# Introduction
This a project built for the SuperWebMiner, which is also a homework of my class. We can use this basic web miner frame to do some web miner works, such as downloading a large quantity of pictures etc. The goal of this project is to enable everyone to start his/her own super mine engine, and at the same time this project pushes me to comprised AI system closer. It would be great for you to give me suggestions on this project, all of us make it better and stronger!
- [Download Source Codes File Folder](https://minhaskamal.github.io/DownGit/#/home?url=https://github.com/Airscker/SuperWebMiner/tree/main/SuperMiner)
- [Command Support](https://airscker.github.io/SuperWebMiner/Command%20Support.html)
- [Document](https://airscker.github.io/SuperWebMiner/document.html)
- [Release Notes](https://airscker.github.io/SuperWebMiner/Release%20Notes.html)
# Copyright
* Author: Airscker
* Last Edited Time: 2022-7
* Latest Edition: 22.3.1.2
* Open source project. Copyright (C) Airscker, airscker@gmail.com, Mozilla Public License Version 2.0
# Basic steps of coding on IDE
Here we give you all the steps and references for build your first engine
### Preparations
- For Python

  Before you import code into our project, you need to download the project in this way:
```python
pip install SuperMiner
```
- For Browser
	- Now you need to install Chrome browser(this project only support chrome currently).
	- Secondly get your chrome's edtion number in Settings(tab 'About Chrome', such as 100.0.4896.88).
	- Then download chrome driver according to your edition number [here](http://chromedriver.storage.googleapis.com/index.html).
	- Move the webdriver.exe into the Scripts root path of python, such as: C:\Python\Python39\Scripts\
### Import
wait until all download threads executed, then open your project, type in:
```python
from SuperMiner import SMiner as SM
```
### Start your first engine
Here we show the basic steps to download Hello world images
- Initialize your engine
```python
Hello_engine=SM.SuperMiner(url='https://cn.bing.com/images/search?q=Hello+world')
```
- Start miner engine
```python
Hello_engine.MineEngine()
```
- Scroll the page to get more images
```python
SM.Basic_Actions(engine=Hello_engine.engine,Obj_index=-2,send_keys=False,rollpage=True)
```
- Get the attributes of the images
```python
Attr=Hello_engine.Attributes('src',Hello_engine.Objects(Class='mimg'))
```
- Download Images
```python
Hello_engine.Download(Attr,data_type='img')
```
- Close engine
```python
Hello_engine.engine.quit()
```
Now you are able to see the images downloaded in 'downloads' file folder, because the network may not be good enough, some images may be crashed, it's just no problem.

To get more details, please see [Document](https://airscker.github.io/SuperWebMiner/document.html), and command support is added since edition 22.2.0.0(R22.2.0.0), to get more details please see [Command Support](https://airscker.github.io/SuperWebMiner/Command%20Support.html)





2022-3-14

We go until we go wrong, then we keep on until we are right

For dream



