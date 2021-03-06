from requests_oauthlib.oauth1_session import OAuth1Session
import tweepy
import config
import json
import os
from dotenv import load_dotenv
load_dotenv()

# トークン等取得
AK = os.environ.get('TWITTER_DOT_API_KEY')
AS = os.environ.get('TWITTER_DOT_API_SECRET_KEY')
AT = os.environ.get('TWITTER_DOT_ACCESS_TOKEN')
ATS = os.environ.get('TWITTER_DOT_ACCESS_TOKEN_SECRET')
BT = os.environ.get('TWITTER_DOT_BEARER_TOKEN')


# Twitterオブジェクトの生成
client = tweepy.Client(BT, AK, AS, AT, ATS)
twitter_api =  OAuth1Session(AK, AS, AT, ATS)

class Twitter:
    def __init__(self, price, cmc_rank, percent_change_24h):
        self.price = price
        self.cmc_rank = cmc_rank
        self.percent_change_24h = percent_change_24h

    ##
    ## ポルカドットの情報をCMCから取得する
    ##
    def tweet_dot_info(self):
         # 前回の時価総額ランキングを取得
        last_cmc_rank, last_tweet_id, last_tweet_content = self.get_last_tweet()
        
        # ツイート内容
        content = self.get_tweet_content(last_cmc_rank)
        print(content)
        
        # 前回ツイート内容と今回ツイート内容を比較
        if last_tweet_content == content:
            # 全く同じ場合空文字を末尾に追加
            content += ' '

        # ツイートを投稿
        res = client.create_tweet(text=content)
        # print(res)
        return last_tweet_id
        
    ##
    ## 前回の時価総額ランキングを取得する
    ##
    def get_last_tweet(self):
        # 過去ツイート取得
        url = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
        params = {'count':5}
        res = twitter_api.get(url, params=params)
        timeline = json.loads(res.text)
        last_cmc_rank = ''
        last_tweet_id = ''

        # ツイート内容加工　5ツイート遡って、最新の時価総額ランキングを調べる
        for i in range(5):
            print("i:" + str(i))
            tweet_content = timeline[i]['text']

            target_end = '位です。'
            idx_end = tweet_content.find(target_end)

            target_start = 'ランキングは'
            idx_start = tweet_content.find(target_start)
            last_cmc_rank = tweet_content[idx_start+len(target_start):idx_end]

            # 時価総額ツイートがあれば、ループ抜ける
            if(idx_end != -1):
                last_tweet_id = int(timeline[i]['id_str'])
                break
        
        print("last_cmc_rank：" + last_cmc_rank)
        return last_cmc_rank, last_tweet_id, tweet_content


    ##
    ## ポルカドットの情報をツイートする
    ##
    def tweet_dot_news(self, news_title, news_url):
        # ツイート内容
        content = '【ポルカドット関連ニュース】\n'
        content +=  f'{news_title}\n\n'
        content +=  '#DOT #暗号資産\n' 
        content +=  f'{news_url}'
        
        print(content)

        # ツイートを投稿
        res = client.create_tweet(text=content)
        # print(res)


    ##
    ## リツイートする
    ##
    def retweet(self, last_tweet_id):
        last_tweet_id = str(last_tweet_id)
        # 検索API叩く , 'since_id':since_id
        url = 'https://api.twitter.com/1.1/search/tweets.json'
        params = {
            'q':config.SEARCH_WORD
            , 'lang':'ja'
            , 'result_type':'recent'
            , 'since_id':last_tweet_id
        }
        res = twitter_api.get(url, params=params)
    
        # 返却値json読み込み
        res = json.loads(res.text)
        news_count = len(res['statuses'])
        res_list = res['statuses']
        res_list_size = len(res_list)

        if (news_count != 0):
        # 取得したツイートを回す
            for res_row in range(res_list_size):
                tweet_id = res_list[res_row]['id_str']
                text = res_list[res_row]['text']
                print('tweet_id:' + tweet_id)
                print('text:' + text)
                print('----------------------------------------------')

                if ('ポルカドット' in text or 'DOT' in text):
                    # リツイートAPI叩く
                    url = 'https://api.twitter.com/1.1/statuses/retweet/' + tweet_id + '.json'

                    # リツイートパラメータ設定
                    params = {
                        'id' : tweet_id
                        ,'include_entities' : ''
                    }

                    # リツイート
                    res = twitter_api.post(url, params=params)


    ##
    ## DM通知
    ##
    # def info_direct_message(self):
    #     params = {("count",3)}
    #     getlist = twitter_api.get("https://api.twitter.com/1.1/direct_messages/events/list.json")
    #     dmlist = json.loads(getlist.text)
    #     for line in dmlist:
    #         if len(line) > 0:
    #             print(line["text"])


    ##
    ## ツイート内容を取得する
    ##
    def get_tweet_content(self, last_cmc_rank):
        content = ''

        if self.percent_change_24h < 0:
            content =  f'現在のポルカドットの時価総額ランキングは{self.cmc_rank}位です。\n'
            content += f'値段は{self.price}円です。\n'
            content += f'これは24時間前に比べて{self.percent_change_24h}%です。\n\n'
            content +=  '#DOT #暗号資産' 

            if self.cmc_rank < int(last_cmc_rank):
                content =  f'【時価総額ランキング上昇！！！】\n'
                content += f'現在のポルカドットの時価総額ランキングは{self.cmc_rank}位です。\n'
                content += f'値段は{self.price}円です。\n'
                content += f'これは24時間前に比べて{self.percent_change_24h}%です。\n\n'
                content +=  '#DOT #暗号資産' 

        elif 0 <= self.percent_change_24h < 6:
            content =  f'現在のポルカドットの時価総額ランキングは{self.cmc_rank}位です。\n'
            content += f'値段は{self.price}円です。\n'
            content += f'これは24時間前に比べて+{self.percent_change_24h}%です。\n\n'
            content +=  '#DOT #暗号資産' 

            if self.cmc_rank < int(last_cmc_rank):
                content =  f'【時価総額ランキング上昇！！！】\n'
                content += f'現在のポルカドットの時価総額ランキングは{self.cmc_rank}位です。\n'
                content += f'値段は{self.price}円です。\n'
                content += f'これは24時間前に比べて+{self.percent_change_24h}%です。\n\n'
                content +=  '#DOT #暗号資産' 
             
        elif 6 <= self.percent_change_24h < 10:
            content = '【いい調子♪】\n'
            content += f'現在のポルカドットの時価総額ランキングは{self.cmc_rank}位です。\n'
            content += f'値段は{self.price}円です。\n'
            content += f'これは24時間前に比べて+{self.percent_change_24h}%です！\n\n'
            content +=  '#DOT #暗号資産' 

        elif 10 <= self.percent_change_24h < 20:
            content = '【きてます！!！】\n'
            content += f'現在のポルカドットの時価総額ランキングは{self.cmc_rank}位です。\n'
            content += f'値段は{self.price}円です。\n'
            content += f'これは24時間前に比べて+{self.percent_change_24h}%です！！\n\n'
            content +=  '#DOT #暗号資産' 

        elif 20 <= self.percent_change_24h < 30:
            content = '【うぉおおぉお仕事辞めてえ！！！！！！】\n'
            content += f'現在のポルカドットの時価総額ランキングは{self.cmc_rank}位です。\n'
            content += f'値段は{self.price}円です。\n'
            content += f'これは24時間前に比べて+{self.percent_change_24h}%です！！\n\n'
            content +=  '#DOT #暗号資産' 

        elif 30 <= self.percent_change_24h < 60:
            content = '【よっしゃあぁあああああ！！！！祭りじゃああぁあ！！！！】\n'
            content += f'現在のポルカドットの時価総額ランキングは{self.cmc_rank}位です。\n'
            content += f'値段は{self.price}円です。\n'
            content += f'これは24時間前に比べて+{self.percent_change_24h}%です！！！\n\n'
            content +=  '#DOT #暗号資産' 

        elif 60 <= self.percent_change_24h < 100:
            content = '【うああああおあああああおおああああああああ！！！！！！！！！】\n'
            content += f'現在のポルカドットの時価総額ランキングは{self.cmc_rank}位です。\n'
            content += f'値段は{self.price}円です。\n'
            content += f'これは24時間前に比べて+{self.percent_change_24h}%です！！！！\n\n'
            content +=  '#DOT #暗号資産' 

        elif 100 <= self.percent_change_24h:
            content = '最高の景色や・・・\n'
            content += f'現在のポルカドットの時価総額ランキングは{self.cmc_rank}位です。\n'
            content += f'値段は{self.price}円です。\n'
            content += f'これは24時間前に比べて+{self.percent_change_24h}%です。\n\n'
            content +=  '#DOT #暗号資産' 

        return content



