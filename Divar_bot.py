from selenium.webdriver.common.keys import Keys
from time import sleep
from selenium import webdriver
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import  WebDriverWait
import os , csv

class Divar:
    def __init__(self,
                 user,
                 city = "tehran",
                 buy_or_rent = "buy",
                 location = "azari",
                 size = "65-200",
                 price = "300000000-5000000000",
                 ) -> None:
        
        self.phone_list = ["",]
        self.links_list = ["",]
        self.size_list = ["",]
        self.year_of_build_list = ["",]
        self.number_of_rooms_list = ["",]
        self.price_list = ["",]
        self.floor_list = ["",]
        self.price_per_meter_list = ["",]
        self.elevator_list = ["",]
        self.parking_list = ["",]
        self.storage_list = ["",]
        self.image_list = ["",]
        

        # put ur username account in your windows
        self.user:str = user
        # you have to sing in into the Divar website with ur phone number to be able to excract the phone numbers 
        user_profile = fr"--user-data-dir=C:\\Users\\{self.user}\AppData\\Local\\Google\\Chrome\\User Data"
        op = webdriver.ChromeOptions()
        op.add_argument("--start-maximize")
        # op.add_argument("--incognito")
        op.add_argument(user_profile)
        op.add_argument('--profile-directory=Default')
        self.driver = webdriver.Chrome(options=op)
        self.city = city
        self.buy_or_rent = buy_or_rent 
        # make a list of all the city on tehran in order to select one 
        self.location = location 
        self.size = size 
        self.price = price
        

    def run_bot(self,image=False):
        self.image = image
        self.driver.get(f"https://divar.ir/s/{self.city}/{self.buy_or_rent}-residential/{self.location}?size={self.size}&price={self.price}&has-photo=true")
        articles = WebDriverWait(self.driver,100).until(EC.visibility_of_all_elements_located((By.TAG_NAME,"article")))

        for article in articles:
            thumb_nail = article.find_element(By.TAG_NAME,"img").get_attribute("src")
            self.image_list.append(thumb_nail) # type:ignore 
            links = article.find_element(By.TAG_NAME,"a")
            link = links.get_attribute("href")
            self.links_list.append(link) # type:ignore 
            name = article.find_element(By.TAG_NAME,"h2").text
            name = name.replace("/","-").replace("\\","-").replace("*","-")
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            self.driver.get(link) # type: ignore
            # new page opens
            # scrap the info of the building
            button = WebDriverWait(self.driver,20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,".kt-button.kt-button--primary.post-actions__get-contact")))
            button.click()
            tel_number = WebDriverWait(self.driver,10).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="app"]/div[1]/div/main/article/div/div[1]/section[1]/div[3]/div[1]/div/div[2]/a')))
            tel = tel_number.get_attribute("href").replace("tel:","").strip()# type: ignore
            self.phone_list.append(tel)

            rows = self.driver.find_elements(By.XPATH,"/html/body/div[1]/div[1]/div/main/article/div/div[1]/section[1]/div[4]/table[1]/tbody/tr")
            for row in rows:
                for i in range(3):
                    info = row.find_elements(By.TAG_NAME,"td")[i]
                    if i == 0 :
                        self.size_list.append(info.text)
                    elif i == 1:
                        self.year_of_build_list.append(info.text)
                    elif i == 2:
                        self.number_of_rooms_list.append(info.text)
            sleep(5)
            full_price = self.driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/article/div/div[1]/section[1]/div[4]/div[2]/div[2]/p")
            self.price_list.append(full_price.text)
            price_per_meter = self.driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/article/div/div[1]/section[1]/div[4]/div[3]/div[2]/p")
            self.price_per_meter_list.append(price_per_meter.text)
            floor_number = self.driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/article/div/div[1]/section[1]/div[4]/div[4]/div[2]/p")
            self.floor_list.append(floor_number.text)
            options_all = self.driver.find_element(By.XPATH,"/html/body/div[1]/div[1]/div/main/article/div/div[1]/section[1]/div[4]/table[2]/tbody")
            options = options_all.find_elements(By.TAG_NAME,"tr")
            for option in options:
                for i in range(3):
                    opt = option.find_elements(By.TAG_NAME,"td")[i]
                    if i == 0 :
                        self.elevator_list.append(opt.text)
                    elif i == 1:
                        self.parking_list.append(opt.text)
                    elif i == 2:
                        self.storage_list.append(opt.text)

            # downloading images
            if self.image == True:
                pic_element = WebDriverWait(self.driver,20).until(EC.visibility_of_element_located((By.XPATH,'//*[@id="app"]/div[1]/div/main/article/div/div[2]/section[1]')))
                pic_num = pic_element.find_element(By.TAG_NAME,"span").get_attribute("innerHTML")
                pic_num = int(pic_num[-1]) # type: ignore
                left_arrow = self.driver.find_element(By.TAG_NAME,"html")
                for i in range(pic_num):
                    image_element = pic_element.find_element(By.TAG_NAME,'img')
                    src = requests.get(image_element.get_attribute("src")) # type:ignore
                    newpath = fr".\divar_data\{name}"
                    if not os.path.exists(newpath):
                        os.makedirs(newpath)
                    with open(fr"{newpath}\{i}.jpg","wb") as f:
                        f.write(src.content)
                    left_arrow.send_keys(Keys.LEFT)
                    
                    sleep(3.5)
                with open(fr"{newpath}\{i}.csv",mode="a",newline="") as f: # type:ignore
                    writer = csv.writer(f)
                    writer.writerow(["Phone Number",tel])
            sleep(5)
            # new page closed
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def get_phones(self):
        return self.phone_list
    def get_links(self):
        return self.links_list
    def get_size(self):
        return self.size_list
    def get_year_of_build(self):
        return self.year_of_build_list
    def get_number_of_rooms_list(self):
        return self.number_of_rooms_list
    def get_price(self):
        return self.price_list
    def get_floor(self):
        return self.floor_list
    def get_price_per_meter(self):
        return self.price_per_meter_list
    def get_elevator(self):
        return self.elevator_list
    def get_parking(self):
        return self.parking_list
    def get_storage(self):
        return self.storage_list
    def get_image(self):
        return self.image_list
    
# div_bot = Divar("Roberick")
# div_bot.run_bot()