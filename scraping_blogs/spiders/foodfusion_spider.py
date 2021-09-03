import scrapy

class FoodFusionDishes(scrapy.Spider):
    name = 'foodfusion'

    start_urls = [
        'https://www.foodfusion.com/'
    ]

    def parse(self, response):
        """
            Main parser to get each category and respective url.

            Only the main and first page of the site is used to
            get the starting point.
        """        
        for cat in response.css('li.menu-item.menu-item-type-taxonomy.menu-item-object-recipe_category a::attr(href)').extract():
            yield response.follow(cat, self.parse_categories)

    def parse_categories(self, response):
        """
            Second stage.
            In this section scrapy loops through all of the pages of
            a given category. Later, it passes each element on each
            page to the function parse_recipes 
        """
        cat_name= response.request.url.replace('https://www.foodfusion.com/recipe-category/', '').split('/')[0]
        for meal in response.css('div.uk-card.uk-card-default.card-border'):
            blog_url = meal.css('div.uk-card-body.ellipsis-text a::attr(href)')[0].extract()
            yield response.follow(blog_url, self.parse_recipes, meta={'cat_name': cat_name})
        try:
            next_page = response.css('a.next-page::attr(href)')[0].extract()
            if next_page is not None:
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse_categories)
        except:
            print('page count reached in %s' % cat_name)

    def parse_recipes(self, response):
        """
            Third and last stage.
            Here is the final destination that collects all the
            data about the recipe and yields(returns) it.

            Using category variables across the functions allows
            us to have category information about the recipes
            since in recipes respective pages there is not an
            information about the category.
        """
        sponsor = ''
        try:
            sponsor = response.css('span.sponsored-img img::attr(src)')[0].extract().strip()
        except:
            print('no sponsor')

        yield {
            'cat_name': response.meta.get('cat_name'),
            'title': response.css('h1.recipe-detail-heading::text').get(),
            'desc': response.css('div.recipe-detail-style p::text').get(),
            'author': response.css('div.behind-camera span::text').get(),
            'post_date': response.css('div.postdate::text').get().replace('Published: ', ''),
            'ingredients': ','.join(response.css('ul.am-ing li::text').getall()),
            'blog_url': response.request.url.strip(),
            'youtube_url': response.css('div.recipe-video iframe::attr(src)')[0].extract(),
            'sponsor': sponsor
        }

# scrapy crawl foodfusion -o foodfusion.csv