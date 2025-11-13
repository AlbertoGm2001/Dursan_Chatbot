import sys 
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
import time
from modules.MainPageCrawler import MainPageCrawler
from dotenv import load_dotenv  
from src.models.CarAd import create_db, remove_db
import glob


load_dotenv()
main_url = os.getenv("MAIN_URL")

def crawl_main_page():
    remove_db()
    create_db()

    #Se borran las imágenes de coches que se tenían
    image_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "frontend", "images", "car_images")
    image_files = glob.glob(os.path.join(image_folder, "*"))
    for image_file in image_files:
        try:
            os.remove(image_file)
        except Exception as e:
            print(f"Error deleting {image_file}: {e}")

    crawler = MainPageCrawler(main_url)
    html = crawler.get_html()
    page_url_list = crawler.get_all_urls(html)

    start_time = time.time()
    max_pages_to_crawl = int(os.getenv("MAX_PAGES_TO_CRAWL"))

    batch_size = 10  # Process pages in batches
    total_ads_collected = 0

    for batch_start in range(0, min(len(page_url_list), max_pages_to_crawl), batch_size):
        batch_end = min(batch_start + batch_size, min(len(page_url_list), max_pages_to_crawl))
        batch_car_ads = []
        
        print(f'Processing batch {batch_start//batch_size + 1}/{(min(len(page_url_list), max_pages_to_crawl) + batch_size - 1)//batch_size}')
        
        for i in range(batch_start, batch_end):
            try:
                print(f'Extracting page {i+1}/{min(len(page_url_list), max_pages_to_crawl)}')
                html = crawler.get_html(page_url_list[i])
                page_ads = crawler.get_page_ads(html)
                
                if not page_ads:  # Skip empty pages
                    print(f'No ads found on page {i+1}, skipping...')
                    continue
                    
                batch_car_ads.extend(page_ads)

            except Exception as e:
                print(f'Error on page {i+1}: {e}')
        
        # Insert batch to database
        if batch_car_ads:
            print(f'Inserting {len(batch_car_ads)} ads from batch {batch_start//batch_size + 1}')
            crawler.insert_car_ads(batch_car_ads)
            total_ads_collected += len(batch_car_ads)
            print(f'Total ads collected so far: {total_ads_collected}')

    end_time = time.time()
    print(f"Execution time: {end_time - start_time:.2f} seconds")
    print(f"Total ads collected: {total_ads_collected}")

if __name__ == "__main__":
    crawl_main_page()
