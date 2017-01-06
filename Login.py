# coding = utf-8
from selenium import webdriver
from tkinter import *
import urllib.request


class WeiboWebLogin(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
    def Login(self):
        global CAPTCHA
        driver = webdriver.PhantomJS(executable_path='phantomjs')  # 放在Script文件中
        driver.get(r'http://weibo.cn/pub/')
        login_botton = driver.find_element_by_link_text('登录')
        login_botton.click()
        print('Login Url：' + driver.current_url)
        driver.find_element_by_name('mobile').send_keys(self.username)
        driver.find_element_by_xpath(r'/html/body/div[2]//input[@type="password"]').send_keys(self.password)
        captcha_img_url = driver.find_element_by_xpath('/html/body/div[2]/form//img').get_attribute('src')
        urllib.request.urlretrieve(captcha_img_url, 'captcha.gif')
        show()
        print('captcha: ' + CAPTCHA)
        driver.find_element_by_name('code').send_keys(CAPTCHA)
        driver.find_element_by_name('submit').click()
        print('Now Url：' + driver.current_url)



root = Tk()
# root.resizable(False,False)
root.title = 'Captcha'
captcha_text = StringVar()
#屏幕居中
# root.update()   # update window ,must do
# curWidth = root.winfo_reqwidth() # get current width
# curHeight = root.winfo_height() # get current height
# scnWidth,scnHeight = root.maxsize() # get screen width and height
# tmpcnf = '%dx%d+%d+%d'%(curWidth,curHeight,
# (scnWidth-curWidth)/2,(scnHeight-curHeight)/2)
# root.geometry(tmpcnf)




def submit():
    global CAPTCHA
    CAPTCHA = captcha_text.get()
    root.destroy()


def show():
    photo = PhotoImage(file='captcha.gif')
    Label(root, image=photo, width=100,height=20).grid(row=0,column=0)
    Entry(root, text=captcha_text).grid(row=1,column=0)
    Button(root, command=submit, text='提交并关闭').grid(row=2,column=0)
    root.mainloop()







if __name__ == '__main__':
    username = input('Username: ')
    password = input('Password: ')
    a = WeiboWebLogin(username, password)
    a.Login()


