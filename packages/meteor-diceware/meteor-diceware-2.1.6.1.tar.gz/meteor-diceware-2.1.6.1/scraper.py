HEADERS = {

			'sec-ch-ua' : r'" Not;A Brand";v="99", "Microsoft Edge";v="91", "Chromium";v="91"' ,
			'sec-ch-ua-mobile' : '?0' ,
			'Upgrade-Insecure-Requests' : '1' ,
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.41 Safari/537.36 Edg/88.0.705.22' ,
			'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}



def retrieve_soup(url):
  
    global HEADERS
  
    from bs4 import BeautifulSoup
    import requests 
    
    return ' '.join(BeautifulSoup(requests.get(url , headers = HEADERS ).content.decode('utf8' , 'ignore'), "html.parser").stripped_strings)
    
def retrieve_selenium(url , driver):
    
    import time 
    from inscriptis import get_text
    
    driver.get(url)
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    
    while True:
        
        lastCount = lenOfPage
        time.sleep(1)
        
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            break 
    
    return get_text(driver.page_source)

def get_driver():
    
        from . import cfg 
        
        assert (cfg.SELENIUM_BINARY is not None) and (cfg.SELENIUM_DRIVER is not None), f"Selenium driver not configured in cfg.py"
    
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        
        chrome_options = Options()
        chrome_options.add_argument("--silent")
        chrome_options.binary_location = cfg.SELENIUM_BINARY 
        
        return webdriver.Chrome(  executable_path = cfg.SELENIUM_DRIVER , chrome_options=chrome_options)