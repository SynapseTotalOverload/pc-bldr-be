from sqlalchemy import select
import logging

from app.models import Product
from app.db.session import SessionLocal
from app.services.keepa import api


def actualize_prices_and_rating():
    with SessionLocal() as db:
        try:
            stm = select(Product)
            products: list[Product] = db.execute(stm).scalars().all()
            products_asins_map = {prod.asin: prod for prod in products}
            products_asins = list(products_asins_map.keys())
            splited_lists_of_products_asins: list[list[Product]] = [products_asins[i:i+100] for i in range(0,len(products_asins),100)]
            for products_list in splited_lists_of_products_asins:
                try:
                    keepa_res = {res["asin"]: res for res in api.query(products_list, stats=1, history=False, rating=True)}
                except Exception as e:
                    logging.warning(f"Error scraping products data, saving already scraped info: {e}")
                    break
                for product_asin in products_list:
                    product = products_asins_map[product_asin]
                    keepa_prod = keepa_res[product_asin]
                    cur_prod_state = keepa_prod["stats_parsed"].get("current")
                    if cur_prod_state:
                        prod_rate = round(cur_prod_state.get("RATING", float(0)), 1) or None
                        prod_price: float = (
                            cur_prod_state.get("AMAZON") or 
                            cur_prod_state.get("NEW") or 
                            cur_prod_state.get("USED") or
                            None
                        )
                        product.rating = prod_rate
                        product.price = prod_price

                db.commit()

        except Exception as e:
            db.rollback()
            logging.error(f"Error while processing prices and ratings from keepa: {e}")


if __name__ == "__main__":
    actualize_prices_and_rating()
