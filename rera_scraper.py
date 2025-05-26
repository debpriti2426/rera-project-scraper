from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Setup Chrome browser
options = webdriver.ChromeOptions()
options.add_argument('--headless') # comment out this line to run in background
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://rera.odisha.gov.in/projects/project-list"
driver.get(url)
wait = WebDriverWait(driver, 20)

# Wait until at least one project card is loaded
wait.until(EC.presence_of_element_located((By.CLASS_NAME, "project_card")))

# Scroll to load dynamic content
driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(2)

projects = driver.find_elements(By.CLASS_NAME, "project_card")[:6]
data = []

for i, project in enumerate(projects):
    try:
        # Click on "View Details" button
        view_button = project.find_element(By.XPATH, ".//button[contains(text(),'View Details')]")
        driver.execute_script("arguments[0].click();", view_button)

        # Wait for modal or navigation
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "details_container")))

        # Extract data from the detail page
        regd_no = driver.find_element(By.XPATH, "//td[contains(text(),'RERA Regd. No.')]/following-sibling::td").text
        project_name = driver.find_element(By.XPATH, "//td[contains(text(),'Project Name')]/following-sibling::td").text
        promoter_name = driver.find_element(By.XPATH, "//a[contains(text(),'Promoter Details')]").click()
        time.sleep(1)

        # Promoter details
        promoter_name = driver.find_element(By.XPATH, "//td[contains(text(),'Company Name')]/following-sibling::td").text
        address = driver.find_element(By.XPATH, "//td[contains(text(),'Registered Office Address')]/following-sibling::td").text
        gst = driver.find_element(By.XPATH, "//td[contains(text(),'GST No.')]/following-sibling::td").text

        # Store data
        data.append({
            "RERA Regd. No": regd_no,
            "Project Name": project_name,
            "Promoter Name": promoter_name,
            "Promoter Address": address,
            "GST No": gst
        })

        # Navigate back
        driver.back()
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "project_card")))

        # Refresh project list after back
        projects = driver.find_elements(By.CLASS_NAME, "project_card")[:6]

    except Exception as e:
        print(f"Error in project {i+1}: {e}")
        continue

driver.quit()

# Save to Excel
df = pd.DataFrame(data)
df.to_excel("rera_projects.xlsx", index=False)
print("Data saved to rera_projects.xlsx")
