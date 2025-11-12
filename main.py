import db_handler as db
import Crawler_articles as crawler

is_test = False

crawler.main(is_test)
db.main()
