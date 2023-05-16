#Google colabo用のライブラリインストールコード
#!pip install pytumblr

import pytumblr
import os

os.environ['CONSUMER_KEY'] = 'your consumer key'
os.environ['CONSUMER_SECRET'] = 'consumer secret'

consumer_key = os.environ.get('CONSUMER_KEY')
consumer_secret = os.environ.get('CONSUMER_SECRET')

# Authenticate via OAuth
client = pytumblr.TumblrRestClient(
  consumer_key,
  consumer_secret
)

# Make the request
tag = "Japanesefestival"  # キーワードを指定
limit = 1  # 取得するポストの数を指定
posts = client.tagged(tag, limit=limit)

# Print the posts
for post in posts:
    print(post)