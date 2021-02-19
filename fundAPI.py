import selenium
from selenium import webdriver	# Allows you to launch/initialise a browser.
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait	 # Allows you to wait for a page to load.
from selenium.webdriver.support import expected_conditions as EC  # Specify what you are looking for on a specific page in order to determine that the webpage has loaded.
from selenium.webdriver.common.by import By	 # Allows you to search for things using specific parameters.
from selenium.common.exceptions import TimeoutException  # Handling a timeout situation.

def get_fund_prices(fundList):

    # Chrome WebDriver Options
    chrome_options = Options()
    # Comment the line below if you would like to watch the kapos-man!
    chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--start-maximized")
    try:
        driver = webdriver.Chrome(executable_path='.\\webDrivers\\chromedriver.exe', options=chrome_options)
    except:
        driver = webdriver.Chrome(executable_path='./webDrivers/chromedriver', options=chrome_options)
    wait = WebDriverWait(driver, 10)

    fundDict = {}
    for fund in fundList:
        # Load the web page
        fundURL = "https://www.tefas.gov.tr/FonAnaliz.aspx?FonKod=" + fund
        driver.get(fundURL)

        fundPage = wait.until(EC.visibility_of_element_located((By.ID, "MainContent_PanelInfo")))
        lastPrice = fundPage.find_element_by_xpath("//div/ul/li[contains(text(),'{}')]/span".format("Son Fiyat"))
        
        fundDict[fund] = {}
        fundDict[fund]["buyRate"] = float(lastPrice.text.replace(',', '.'))
        fundDict[fund]["sellRate"] = float(lastPrice.text.replace(',', '.'))
    
    driver.quit()
    return fundDict