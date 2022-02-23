import scrapy
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from imdb.spiders.scrape_title import ScrapeTitleSpider
from imdb.spiders.get_titles_ids import GetTitlesIdsSpider
from multiprocessing import Process, Queue

# settings = get_project_settings()
# configure_logging(settings)
# runner = CrawlerRunner(settings)
# process = CrawlerProcess(get_project_settings())

imdb_ids = [
    "tt0120794",
    "tt2953050",
    "tt4574334"
]    

def run_spider(spider, imdb_id):
    def f(q):
        try:
            settings = get_project_settings()
            configure_logging(settings)
            runner = CrawlerRunner(settings)
            deferred = runner.crawl(spider, ID=imdb_id)
            deferred.addBoth(lambda _: reactor.stop())
            reactor.run()
            q.put(None)
        except Exception as e:
            q.put(e)

    q = Queue()
    p = Process(target=f, args=(q,))
    p.start()
    result = q.get()
    p.join()

    if result is not None:
        raise result

for imdb_id in imdb_ids:
    run_spider(ScrapeTitleSpider, imdb_id)





# for imdb_id in imdb_ids:
#     process.crawl(ScrapeTitleSpider, ID=imdb_id)

# process.start()
#process.join()





# def crawl(runner, imdb_id):
#     d = runner.crawl(ScrapeTitleSpider, ID=imdb_id)
#     #d.addBoth(sleep)
#     d.addBoth(lambda _: crawl(runner, imdb_id))
#     return d


# for imdb_id in imdb_ids:
#     runner = CrawlerRunner(get_project_settings())
#     crawl(runner, imdb_id)
#     reactor.run()

# print("OUT OF THE LOOP")
# reactor.stop()





# @defer.inlineCallbacks
# def crawl_titles_ids():
#     yield runner.crawl(GetTitlesIdsSpider, GENRE="comedy")
#     #yield runner.crawl(ScrapeTitleSpider, ID="tt4574334")
#     reactor.stop()

# @defer.inlineCallbacks
# def crawl_scrape_title(imdb_id):
#     yield runner.crawl(ScrapeTitleSpider, ID=imdb_id)
#     reactor.stop()

# def run_scrape_title(imdb_id):
#     crawl_scrape_title(imdb_id)
#     reactor.run()
    
# run_scrape_title("tt2953050")
# run_scrape_title("tt4574334")
