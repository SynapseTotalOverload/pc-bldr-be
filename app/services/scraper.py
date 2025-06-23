from bs4 import BeautifulSoup, ResultSet, Tag
from app.schemas.attributes import (
    BaseAttrsSchema, 
    CPUAttributesSchema, 
    CPUCoolerAttributesSchema, 
    MotherboardAttributesSchema,
    RAMAttributesSchema,
    StorageAttributesSchema,
    GPUAttributesSchema,
    PowerSupplyAttributesSchema,
    CaseAttributesSchema,
)
from app.models import (
    BaseAttrsModel,
    CPUAttributes, 
    CPUCoolerAttributes, 
    MotherboardAttributes,
    RAMAttributes,
    StorageAttributes,
    GPUAttributes,
    Product, 
    PowerSupplyAttributes,
    CaseAttributes
)
from app.db.session import SessionLocal
from app.schemas.product import ProductCreate


CATEGORIES = [
    "/processor/", 
    "/cpu-cooler/", 
    "/motherboard/", 
    "/ram/", 
    "/storage/", 
    "/graphics-card/", 
    "/power-supply/", 
    "/case/",
]


class PcBuilderScraper:
    schema_to_model_mapping: dict[type[BaseAttrsSchema],type[BaseAttrsModel]] = {
        CPUAttributesSchema: CPUAttributes,
        CPUCoolerAttributesSchema: CPUCoolerAttributes,
        MotherboardAttributesSchema: MotherboardAttributes,
        RAMAttributesSchema: RAMAttributes,
        StorageAttributesSchema: StorageAttributes,
        GPUAttributesSchema: GPUAttributes,
        PowerSupplyAttributesSchema: PowerSupplyAttributes,
        CaseAttributesSchema: CaseAttributes,
    }

    def scrape_components(self, html: str, attrs_schema: type[BaseAttrsSchema]):
        soup = BeautifulSoup(html, "lxml")
        products_divs = soup.select("tbody > tr")
        products = self._get_processed_products_and_their_attrs(products_divs, attrs_schema)

        attrs_model = self.schema_to_model_mapping[attrs_schema]
        self._add_all_products_and_their_attrs_to_db(products, attrs_model)

    def _get_processed_products_and_their_attrs(self, products_divs: ResultSet[Tag], attrs_schema: type[BaseAttrsSchema]) -> list[tuple[Product,CPUAttributesSchema]]:
        products: list[tuple[Product,BaseAttrsSchema]] = list()
        for product_tag in products_divs:
            product_obj = self._get_product_object_from_product_tag(product_tag)
            attrs_schema_obj = self._get_attrs_schema_from_product_tag(product_tag, attrs_schema)
            products.append(
                (
                    product_obj, 
                    attrs_schema_obj
                )
            )
        return products

    def _get_product_object_from_product_tag(self, product_tag: Tag) -> Product:
        title = product_tag.select_one("td.comp-details > div.table_title > a").text.strip()
        asin = product_tag.select_one("td > a.btn.btn-primary.component-btn")["href"].split("/")[-1].split("?")[0]
        product_schema = ProductCreate(asin=asin, title=title)
        return Product(**product_schema.model_dump())

    def _get_attrs_schema_from_product_tag(self, product_tag: ResultSet[Tag], attrs_schema: type[BaseAttrsSchema]) -> BaseAttrsSchema:
        comp_details = product_tag.select("td.comp-details > span > div > div.detail__name")
        attrs_mapping: dict[str,any] = dict()
        for detail in comp_details:
            attrs_mapping[detail.text] = detail.find_next("div").text.strip()

        if attrs_schema is CPUAttributesSchema:
            mem = attrs_mapping["Memory Type:"].split(" - ")
            attrs_mapping["Memory Type:"] = mem[0]
            attrs_mapping["Memory Speed:"] = int(mem[1][:4])
            attrs_mapping["Cores:"] = int(attrs_mapping["Cores:"])
            attrs_mapping["Threads:"] = int(attrs_mapping["Threads:"])
        elif attrs_schema is CPUCoolerAttributesSchema:
            fan_rpm = list(
                attrs_mapping["Fan RPM:"]
                .lower()
                .replace(" to ", " ")
                .replace(" - ", " ")
                .replace("rpm", "")
                .replace("&nbsp;rpm", "")
                .strip()
                .split()
            )
            noise_lvl = list(
                attrs_mapping["Noise Level:"]
                .lower()
                .replace(" to ", " ")
                .replace(" - ", " ")
                .replace("dba", "")
                .replace("db", "")
                .replace("&nbsp;dba", "")
                .replace("&nbsp;db", "")
                .strip()
                .split()
            )
            none_ = {"n/a", "none", "na", ""}
            
            if not len(noise_lvl): 
                attrs_mapping["Noise Level:"] = None
                attrs_mapping["Noise Level Max:"] = None
            elif noise_lvl[0] in none_:
                attrs_mapping["Noise Level:"] = None
                attrs_mapping["Noise Level Max:"] = None
            else:
                attrs_mapping["Noise Level:"] = float(noise_lvl[0])
                attrs_mapping["Noise Level Max:"] = float(noise_lvl[-1])

            if not len(fan_rpm): 
                attrs_mapping["Fan RPM:"] = None
                attrs_mapping["Fan RPM Max:"] = None
            elif fan_rpm[0] in none_:
                attrs_mapping["Fan RPM:"] = None
                attrs_mapping["Fan RPM Max:"] = None
            else:
                attrs_mapping["Fan RPM:"] = int(fan_rpm[0])
                attrs_mapping["Fan RPM Max:"] = int(fan_rpm[-1])
        elif attrs_schema is MotherboardAttributesSchema:
            attrs_mapping["Memory Slots:"] = int(
                attrs_mapping["Memory Slots:"]
                .lower()
                .replace("&nbsp;", " ")
                .replace("\xa0", " ")
                .replace(" slots", "")
                .strip()
            )
            attrs_mapping["Max Memory Support:"] = int(
                attrs_mapping["Max Memory Support:"]
                .lower()
                .replace("&nbsp;", " ")
                .replace("\xa0", " ")
                .replace(" gb", "")
                .strip()
            )
        elif attrs_schema is RAMAttributesSchema:
            attrs_mapping["RAM Size:"] = (
                attrs_mapping["RAM Size:"]
                .lower()
                .replace("&nbsp;", " ")
                .replace("\xa0", " ")
                .replace("gb", "")
                .strip()
            )
            attrs_mapping["RAM Speed:"] = (
                attrs_mapping["RAM Speed:"]
                .lower()
                .replace("&nbsp;", " ")
                .replace("\xa0", " ")
                .replace("mhz", "")
                .strip()
            )
            quantity = (
                attrs_mapping["Quantity:"]
                .lower()
                .replace("&nbsp;", " ")
                .replace("\xa0", " ")
                .replace("gb", "")
                .strip()
                .split(" x ")
            )
            attrs_mapping["Quantity:"] = quantity[0]
            attrs_mapping["Unit Ram Size:"] = quantity[1]
        elif attrs_schema is StorageAttributesSchema:
            capacity: str = (
                attrs_mapping["Capacity:"]
                .lower()
                .replace("&nbsp;", "")
                .replace("\xa0", "")
                .replace(" ", "")
                .strip()
            )
            if capacity.endswith("tb"):
                capacity = capacity.replace("tb", "")
                attrs_mapping["Capacity:"] = int(capacity.split(".")[0])*1000 if capacity else None
            else:
                capacity = capacity.replace("gb", "")
                attrs_mapping["Capacity:"] = int(capacity.split(".")[0]) if capacity else None

            cache_mem = (
                attrs_mapping["Cache Memory:"]
                .lower()
                .replace("&nbsp;", " ")
                .replace("\xa0", " ")
                .strip()
                .split()
            )
            attrs_mapping["Cache Memory:"] = cache_mem[0] if cache_mem else None
        elif attrs_schema is GPUAttributesSchema:
            attrs_mapping["Memory:"] = float(
                attrs_mapping["Memory:"]
                .lower()
                .replace("&nbsp;", "")
                .replace("\xa0", "")
                .replace(" ", "")
                .strip()
                .replace("gb", "")
            )
            length = (
                attrs_mapping["Length:"]
                .lower()
                .replace("&nbsp;", "")
                .replace("\xa0", "")
                .replace(" ", "")
                .replace("w", "")
                .replace("mm", "")
                .replace("none", "")
                .strip()
                .split(".")[0]
            )
            attrs_mapping["Length:"] = int(length) if length else None
            base_clock = (
                attrs_mapping["Base Clock:"]
                .lower()
                .replace("&nbsp;", "")
                .replace("\xa0", "")
                .replace(" ", "")
                .replace("none", "")
                .strip()
                .replace("mhz", "")
            )
            base_clock = int(base_clock) if base_clock else None
            attrs_mapping["Base Clock:"] = base_clock
            clock_speed = (
                attrs_mapping["Clock Speed:"]
                .lower()
                .replace("none", "")
                .replace("&nbsp;", "")
                .replace("\xa0", "")
                .replace("\u200e", "")
                .replace(" ", "")
                .strip()
                .replace("mhz", "")
            )
            clock_speed = int(float(clock_speed.replace("ghz", ""))*1000) if clock_speed.endswith("ghz") else clock_speed
            attrs_mapping["Clock Speed:"] = int(clock_speed) if clock_speed else attrs_mapping["Base Clock:"]
        elif attrs_schema is PowerSupplyAttributesSchema:
            power = (
                attrs_mapping["Power:"]
                .lower()
                .replace("&nbsp;", "")
                .replace("\xa0", "")
                .replace(" ", "")
                .replace("w", "")
                .strip()
            )
            attrs_mapping["Power:"] = int(power) if power else None

        return attrs_schema(**attrs_mapping)

    def _add_all_products_and_their_attrs_to_db(self, products: list[tuple[Product,BaseAttrsSchema]], attrs_model: type[BaseAttrsModel]) -> None:
        with SessionLocal() as db:
            try:
                for product, attrs in products:
                    db.add(product)
                    db.flush([product,])
                    attrs = attrs_model(product_id=product.id, **attrs.model_dump())
                    db.add(attrs)
                db.commit()
            except Exception as e:
                db.rollback()
                raise(e)


def _read_html_file(filename: str) -> str:
    with open(filename, encoding="utf-8") as f:
        raw_data = f.read()
    return raw_data


a = PcBuilderScraper().scrape_components(_read_html_file("Choose a Case - PC Builder.html"), CaseAttributesSchema)
