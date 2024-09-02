from musinsa.product_info_crawling import get_musinsa_product_info
from musinsa.product_day_price import get_product_price
from musinsa.products_num_by_category import extract_product_num_from_categoryinfo
def main():
    # get_musinsa_product_info()
    extract_product_num_from_categoryinfo()
    # get_product_price()
    
if __name__ == "__main__":
    main()
