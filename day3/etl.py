import time
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

def run_dantri_to_csv():
    # ==========================================
    # BƯỚC 1: EXTRACT 
    # ==========================================
    print("\n [EXTRACT] Đang khởi động Chrome để cào Dân Trí...")
    driver = webdriver.Chrome() 
    driver.get("https://dantri.com.vn")
    time.sleep(30)

    articles = driver.find_elements(By.CSS_SELECTOR, "h3.article-title a")
    print(f"   -> Đã quét thấy {len(articles)} bài báo trên màn hình.")

    # ==========================================
    # BƯỚC 2: TRANSFORM
    # ==========================================
    print(" [TRANSFORM] Đang bóc tách và làm sạch dữ liệu...")
    clean_data = []
    
    for article in articles:
        title = article.text.strip()
        link = article.get_attribute("href")
        
        if title and link:
            if not link.startswith("http"):
                link = "https://dantri.com.vn" + link
                
            clean_data.append({
                "Tiêu đề": title,
                "Đường dẫn": link
            })
            
    driver.quit()
    print(f"   -> Đã làm sạch và giữ lại được {len(clean_data)} bài báo hợp lệ.")

    # ==========================================
    # BƯỚC 3: LOAD 
    # ==========================================
    if clean_data:
        print(" [LOAD] Đang xuất dữ liệu ra file CSV...")
        df = pd.DataFrame(clean_data) 
        df.to_csv("dantri_news.csv", index=False, encoding='utf-8-sig')
        
        print(" HOÀN THÀNH! Mời bạn mở file 'dantri_news.csv' để xem thành quả.")
    else:
        print(" Không có dữ liệu nào để lưu.")

if __name__ == "__main__":
    run_dantri_to_csv()