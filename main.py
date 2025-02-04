import os
import smtplib
from apscheduler.schedulers.blocking import BlockingScheduler
from urllib.parse import urlencode
from dotenv import load_dotenv
from datetime import datetime
import csv
from webscraper import scrape_urls

load_dotenv()

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") # GMail App Password
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SEEN_FILE = "seen_listings.txt"
CARS_FILE = "cars.csv"


def read_cars_csv(file_path):
    cars_list = []

    with open(file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=',')  # Assuming tab-separated values
        for row in reader:
            car_dict = {
                'brand': row['BRAND'],
                'model': row['MODEL'],
                'from_year': int(row['YEAR_FROM']),
                'to_year': int(row['YEAR_TO']),
                'from_mileage': int(row['MILEAGE_FROM']),
                'to_mileage': int(row['MILEAGE_TO']),
                'from_price': int(row['PRICE_FROM']),
                'to_price': int(row['PRICE_TO']),
                'tax_deductible': int(row['TAX_DEDUCTIBLE'])
            }
            cars_list.append(car_dict)

    return cars_list

def build_search_url(car):
    """Builds StandVirtual search URL based on car filters"""
    base_path = f"https://www.standvirtual.com/carros/{car['brand']}/{car['model']}/desde-{car['from_year']}"

    query_params = {
        'search[filter_float_first_registration_year:to]': car['to_year'],
        'search[filter_float_mileage:from]': car['from_mileage'],
        'search[filter_float_mileage:to]': car['to_mileage'],
        'search[filter_float_price:from]': car['from_price'],
        'search[filter_float_price:to]': car['to_price'],
        'search[filter_enum_tax_deductible]': car['tax_deductible'],
    }

    return f"{base_path}?{urlencode(query_params)}"



def send_email_notification(new_listings):
    """Sends email notification via Gmail SMTP"""
    subject = "New Car Listings Found that Match Your Criteria"
    body = "\n".join([f"{listing['name']} - {listing['price']}€ - {listing['mileage']} km - {listing['year']} - {listing['url']}" for listing in new_listings])
    message = f"Subject: {subject}\n\n{body}"

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.encode('utf-8'))
        print("Notification email sent successfully")
    except Exception as e:
        print(f"Error sending email: {e}")


def check_listings():
    """Main job function to check for new listings"""
    # print date and time of execution
    print(f"{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - Starting listing check...")

    # Read seen listings
    try:
        with open(SEEN_FILE, 'r') as f:
            seen = set(line.strip() for line in f)
    except FileNotFoundError:
        seen = set()

    try:
        CARS = read_cars_csv(CARS_FILE)
    except FileNotFoundError:
        raise FileNotFoundError(f"File {CARS_FILE} not found")

    # Process each car search
    url_list = [build_search_url(car) for car in CARS]
    try:
        listings_info = scrape_urls(url_list)
        new_listings = [listing for listing in listings_info if listing['url'] not in seen]
    except Exception as e:
        print(f"Error scraping listings: {e}")
        return

    # Process new listings
    if new_listings:
        new_listings = list({frozenset(d.items()): d for d in new_listings}.values())
        print(f"Found {len(new_listings)} new listings")
        send_email_notification(new_listings)

        # Update seen listings
        seen.update(listing['url'] for listing in new_listings)
        with open(SEEN_FILE, 'w') as f:
            f.write("\n".join(seen))
        print("Updated seen listings file")
    else:
        print("No new listings found")



if __name__ == "__main__":
    # Initialize scheduler
    scheduler = BlockingScheduler()
    scheduler.add_job(check_listings, 'cron', minute='*/30')

    print("Starting scheduler...")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped")