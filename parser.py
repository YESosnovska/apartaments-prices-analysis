import csv
import dataclasses
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement

_driver: WebDriver | None = None


def get_driver() -> WebDriver:
    return _driver


def set_driver(new_driver: WebDriver) -> None:
    global _driver
    _driver = new_driver


@dataclass
class Apartment:
    num_of_rooms: int
    area: float
    living_area: float
    kitchen_area: float
    floor: int
    floors_in_house: int
    year_of_building: int
    price: float


APARTMENT_FIELDS = [field.name for field in dataclasses.fields(Apartment)]


def parse_single_apartment(apartment: WebElement) -> Apartment:
    try:
        num_of_rooms = int(apartment.find_element(
            By.XPATH,
            './/div[contains(@class, "RealtyPropertiesItem_text__SR8u") and contains(text(), "кімн")]'
        ).text.strip().split()[0])

        area_text = apartment.find_elements(
            By.CLASS_NAME,
            "RealtyCard_grid__3E92Y"
        )[0].find_elements(By.CLASS_NAME, "RealtyCard_property__k_UqN")[2].find_element(By.CLASS_NAME,
                                                                                        "RealtyPropertiesItem_text__SR8u_").text.split(
            "/")
        area = float(area_text[0].strip())
        living_area = float(area_text[1].strip().replace("-", "0"))
        kitchen_area = float(area_text[2].strip().replace(" м²", ""))

        floor_info = apartment.find_element(
            By.XPATH,
            './/div[contains(@class, "RealtyPropertiesItem_text__SR8u") and contains(text(), "поверх")]'
        ).text.split(" ")

        floor = int(floor_info[1])
        floors_in_house = int(floor_info[3])

        year_of_building = int(apartment.find_elements(
            By.CLASS_NAME, "RealtyCard_property__k_UqN"
        )[5].find_element(By.CLASS_NAME, "RealtyPropertiesItem_text__SR8u_").text.split(" ")[0])

        price_per_square = float(apartment.find_element(
            By.CLASS_NAME, "RealtyCard_priceSqm__zATUX"
            ).text.split("$")[0].strip().replace(" ", ""))

        price = price_per_square * area

        return Apartment(
            num_of_rooms=num_of_rooms,
            area=area,
            living_area=living_area,
            kitchen_area=kitchen_area,
            floor=floor,
            floors_in_house=floors_in_house,
            year_of_building=year_of_building,
            price=price
        )
    except Exception:
        return Apartment(
            num_of_rooms=0,
            area=0,
            living_area=0,
            kitchen_area=0,
            floor=0,
            floors_in_house=0,
            year_of_building=0,
            price=0
        )


def get_page_apartments(page: WebDriver) -> list[Apartment]:
    apartments = page.find_elements(By.CLASS_NAME, "RealtyCard_content__uZgzE")
    return [parse_single_apartment(apartment) for apartment in apartments]


def get_apartments(page_url: str) -> list[Apartment]:
    driver = get_driver()
    all_apartments = []
    page_number = 1

    while True:
        paginated_url = f"{page_url}?page={page_number}"
        driver.get(paginated_url)
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//button[.//span[contains(text(), "$")]]'))
            )
            driver.find_element(By.XPATH, '//button[.//span[contains(text(), "$")]]').click()

            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "RealtyCard_content__uZgzE"))
                )
            except Exception:
                break

        except Exception:
            break

        apartments_on_page = get_page_apartments(driver)

        if not apartments_on_page:
            break

        all_apartments.extend(apartments_on_page)
        page_number += 1

    driver.quit()
    return all_apartments


def write_apartment_to_csv(apartments: [Apartment], file_name: str) -> None:
    with open(file_name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(APARTMENT_FIELDS)
        writer.writerows([dataclasses.astuple(apartment) for apartment in apartments])


def get_all_apartments() -> None:
    with webdriver.Chrome() as driver:
        set_driver(driver)
        write_apartment_to_csv(get_apartments(""), "")


if __name__ == "__main__":
    get_all_apartments()
