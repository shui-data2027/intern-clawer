from framework import BaseSpider, CrawlResult
from framework.models import money_to_cents
from bs4 import BeautifulSoup
import re
import time

class CandidateSpider(BaseSpider):
    platform = "evaless-us"

    default_headers = {
        **BaseSpider.default_headers,
        "referer": "https://evaless.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "accept-language": "en-US,en;q=0.9",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }

    def iter_category_seeds(self, input_seeds):
        """爬虫起始入口：全站全部商品集合页"""
        start_list_url = "https://evaless.com/collections/all"
        return [start_list_url]

    def parse_list(self, html_text, seed, final_url):
        print("页面长度：", len(html_text))
        print("页面前300字符：", html_text[:300])
        soup = BeautifulSoup(html_text, "html.parser")
        detail_urls = []

        # 适配Evaless真实商品卡片a标签
        product_links = soup.select("a.ProductCard__Link")
        for a in product_links:
            path = a.get("href")
            if path:
                full_url = f"https://evaless.com{path}"
                detail_urls.append(full_url)

        # 分页按钮适配
        next_page_url = None
        next_btn = soup.select_one("div.Pagination__NavItem--next a")
        if next_btn:
            next_href = next_btn.get("href")
            next_page_url = f"https://evaless.com{next_href}"

        return detail_urls, next_page_url

    def parse_detail(self, html_text, seed, final_url) -> CrawlResult:
        soup = BeautifulSoup(html_text, "html.parser")
        result = CrawlResult()
        time.sleep(0.3)

        # SPU基础信息
        spu = {}
        match = re.search(r"/products/([^?]+)", final_url)
        spu["spu_id"] = match.group(1) if match else "unknown"
        spu["platform"] = self.platform
        spu["source_url"] = final_url

        title_ele = soup.select_one("h1.ProductMeta__Title")
        spu["title"] = title_ele.get_text(strip=True) if title_ele else ""

        brand_ele = soup.select_one("a.ProductMeta__VendorLink")
        spu["brand"] = brand_ele.get_text(strip=True) if brand_ele else "Evaless"

        # 图片
        img_eles = soup.select("img.ProductGallery__Image")
        imgs = []
        for img in img_eles:
            src = img.get("data-src") or img.get("src")
            if src:
                if src.startswith("//"):
                    src = "https:" + src
                imgs.append(src)
        spu["main_image"] = imgs[0] if imgs else ""
        spu["images"] = imgs

        desc_ele = soup.select_one("div.ProductDescription__Content")
        spu["description"] = desc_ele.get_text(strip=True) if desc_ele else ""

        # 分类
        bread = soup.select("nav.Breadcrumb a")
        spu["category"] = [b.get_text(strip=True) for b in bread if b.get_text(strip=True)]

        # 颜色SKC分组
        color_variants = soup.select("fieldset.VariantOptionGroup")
        if not color_variants:
            color_variants = [soup]

        for color_block in color_variants:
            skc = {}
            color_label = color_block.select_one("legend.VariantOptionGroup__Label")
            color_name = color_label.get_text(strip=True) if color_label else "Default"
            skc["color_name"] = color_name
            skc["skc_id"] = f"{spu['spu_id']}_{color_name.replace(' ','-')}"
            skc["spu_id"] = spu["spu_id"]
            sku_list = []

            # 尺码SKU
            size_radios = color_block.select("input.VariantRadio")
            for radio in size_radios:
                sku = {}
                var_id = radio.get("value")
                sku["sku_id"] = f"{skc['skc_id']}_{var_id}"
                sku["skc_id"] = skc["skc_id"]
                sku["spu_id"] = spu["spu_id"]

                size_label = radio.find_next_sibling("label")
                sku["size"] = size_label.get_text(strip=True) if size_label else ""

                # 价格
                sale_price_ele = soup.select_one("span.Price__Sale")
                orig_price_ele = soup.select_one("span.Price__Compare")
                sale_price = re.search(r"\$(\d+\.?\d*)", sale_price_ele.get_text()) if sale_price_ele else None
                orig_price = re.search(r"\$(\d+\.?\d*)", orig_price_ele.get_text()) if orig_price_ele else None

                sku["price_cents"] = money_to_cents(float(sale_price.group(1))) if sale_price else 0
                sku["original_price_cents"] = money_to_cents(float(orig_price.group(1))) if orig_price else sku["price_cents"]

                # 库存
                sku["stock"] = 0 if radio.get("disabled") else 999
                sku_list.append(sku)

            skc["skus"] = sku_list
            result.add_spu(spu)
            result.add_skc(skc)
            for sku in sku_list:
                result.add_sku(sku)
        return result
