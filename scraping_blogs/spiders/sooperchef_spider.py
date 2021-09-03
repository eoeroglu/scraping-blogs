import scrapy

class SooperChef(scrapy.Spider):
    name = 'sooperchef'

    start_urls = [
        'https://www.sooperchef.pk/other-recipes'
    ]

    def parse(self, response):
        for cat in response.css('h3.item-title'):
            yield response.follow(cat.css('a::attr(href)')[0].extract(), self.parse_categories, meta={'cat_name':cat.css('a::text').get()})
            
    def parse_categories(self, response):
        cat_name = response.request.url.split('/')[-1]
        for recipe in response.css('h1.item-title'):
            blog_url = recipe.css('a::attr(href)')[0].extract()
            yield response.follow(blog_url, self.parse_recipes, meta={'cat_name': cat_name})
        try:
            next_page = response.css('a.page-link::attr(href)')[-1].extract()
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse_categories)
        except:
            print('page count reached in %s' % cat_name)

    def parse_recipes(self, response):
        cat_name = response.meta.get('cat_name')
        try:
            prep,cook,serve = response.css('div.feature-sub-title::text')[0].getall()[0],response.css('div.feature-sub-title::text')[1].getall()[0],response.css('div.feature-sub-title::text')[2].getall()[0]
        except:
            prep,cook,serve = '','',''
        try:
            des = [val for val in response.css('div.tab-pane div div::text').getall() if ('  ' not in val) & (' .' not in val)]
        except:
            des = ''
        yield {
            'cat_name': cat_name,
            'recipe_name': response.css('h1.item-title::text').get(),
            'author': response.css('li.single-meta span::text').get(),
            'date': response.css('li.single-meta a::text').get(),
            'stars': response.css('ul.item-rating span::text').get().strip(),
            'blow_link': response.request.url,
            'youtube_link': response.css('iframe.ifrmae-mobile-view::attr(src)')[0].extract(),
            'prep_time': prep,
            'cook_time': cook,
            'serving': serve,
            'description': des
        }