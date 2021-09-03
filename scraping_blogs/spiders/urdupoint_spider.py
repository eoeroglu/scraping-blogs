import scrapy

def parse_recipe_info(info_list):
    prep_time = ''
    cook_time = ''
    servings = ''
    rate_count = ''
    calories = ''
    try:
        if len(info_list) == 9:
            prep_time = info_list[0]
            cook_time = info_list[2]
            servings = info_list[4]
            rate_count = info_list[6]
            calories = ''
        elif len(info_list) == 11:
            prep_time = info_list[0]
            cook_time = info_list[2]
            servings = info_list[4]
            rate_count = info_list[8]
            calories = info_list[6]
        elif len(info_list) == 3:
            prep_time =''
            cook_time =''
            servings = ''                
            rate_count = info_list[0]
            calories = ''
        else:
            prep_time = ''
            cook_time = ''
            servings = ''
            rate_count = ''
            calories = ''
    except:
        pass
    return prep_time, cook_time, servings, rate_count, calories
        

class UrduPoint(scrapy.Spider):
    name = 'urdupoint'

    start_urls = [
        'https://www.urdupoint.com/cooking/'
    ]

    def parse(self, response):
        for cat in response.css('a.txt_white.full.db.pad10.bsbb'):
            if cat.css('::attr(title)').extract() == []:
                cat_name = cat.css('span::text').get()
            else:
                cat_name = cat.css('::attr(title)')[0].extract()
            cat_link = cat.css('::attr(href)')[0].extract().replace('.html', '/1.html')
            yield response.follow(cat_link, self.parse_categories, meta={'cat_name':cat_name})

    def parse_categories(self, response):
        cat_name = response.meta.get('cat_name')
        for recipe in response.css('div.cooking_list'):
            recipe_link = recipe.css('a.fwn::attr(href)')[0].extract()
            yield response.follow(recipe_link, self.parse_recipes, meta={'cat_name':cat_name})
        try:
            if response.request.url != response.css('ul.pagination li a::attr(href)')[-2].extract():
                next_page = response.css('ul.pagination li a::attr(href)')[-2].extract()
                if next_page is not None:
                    next_page = response.urljoin(next_page)
                    yield scrapy.Request(next_page, callback=self.parse_categories, meta={'cat_name':cat_name})
            else:
                print('page count reached in %s' % cat_name)
        except:
            print('there are no pages in %s' % cat_name)
    
    def parse_recipes(self, response):
        cat_name = response.meta.get('cat_name')
        prep_time, cook_time, servings, rate_count, calories = parse_recipe_info(response.css('div.ac span::text').getall())
        yield {
            'cat_name':cat_name,
            'recipe_name':response.css('div.main_bar h1::text').get(),
            'rating':response.css('span.rating::attr(data-default-rating)').extract_first(),
            'recipe_no':response.request.url[response.request.url.rfind('-')+1:response.request.url.find('.html')],
            'prep_time':prep_time,
            'cook_time':cook_time,
            'blog_url':response.request.url,
            'servings':servings,
            'rate_count':rate_count,
            'calories':calories
        }

        # Elapsed Time: ~50 mins