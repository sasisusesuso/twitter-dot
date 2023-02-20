import scraping as sp
import twitter as tw
import line as ln

def main():
    try:
        # 値段、時価総額ランクを取得  
        scraping = sp.Scraping()
        price, cmc_rank, percent_change_24h = scraping.get_dot_info()
  
        # BITTIMESの記事を取得
        bittimes_update_flg, bittimes_news_title, bittimes_news_url = scraping.get_bittimes_news()
        
        # BITTIMESの記事をツイートする
        twitter = tw.Twitter(price, cmc_rank, percent_change_24h)
        if bittimes_update_flg == True:
            twitter.tweet_dot_news(bittimes_news_title, bittimes_news_url)
        
        # Yahoo記事を取得
        yahoo_update_flg, yahoo_news_title, yahoo_news_url = scraping.get_yahoo_news()
        
        # Yahoo記事をツイートする
        if yahoo_update_flg == True:
            twitter.tweet_dot_news(yahoo_news_title, yahoo_news_url)

        # ポルカドットの情報をツイートする
        last_tweet_id = twitter.tweet_dot_info()

        # リツイートする
        twitter.retweet(last_tweet_id)

        # DMをLINEで通知する
        # twitter.info_direct_message()

    except Exception as e:
        print(e)
        
        # エラー内容LINE通知
        line = ln.Line()
        line.send_message(e)

if __name__ == '__main__':
    main()
