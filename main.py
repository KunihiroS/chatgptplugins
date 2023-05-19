import pytumblr
import os
import openai
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

# Create a credential object using DefaultAzureCredential
credential = DefaultAzureCredential()

# Create a secret client using the credential and the key vault url
key_vault_url = "https://<your-key-vault-name>.vault.azure.net"
secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

# Retrieve the secrets
consumer_key = secret_client.get_secret('CONSUMER_KEY')
consumer_secret = secret_client.get_secret('CONSUMER_SECRET')
openai_api_key = secret_client.get_secret('OPENAI_API_KEY')

# Use the secrets in your program
openai.api_key = openai_api_key.value
client = pytumblr.TumblrRestClient(
  consumer_key.value,
  consumer_secret.value
)

def process(prompt):
    # Extract relevant tags from the user's prompt
    tags = extract_tags(prompt)

    posts_data = []
    for tag in tags:
        # Make the request
        limit = 1  # 取得するポストの数を指定
        posts = client.tagged(tag, limit=limit)

        # Extract relevant information from the posts and add to posts_data
        for post in posts:
            posts_data.append(extract_post_data(post))

    # Select the most relevant post
    # selected_post = select_post(prompt, posts_data)
    selected_post = select_post(posts_data)

    # Return a user-friendly string
    return f"Here's a post I found: {selected_post['summary']}. You can view the post here: {selected_post['short_url']}"

def extract_tags(prompt):
    # Send the prompt to the OpenAI API
    response = openai.Completion.create(
      engine="text-davinci-003",
      prompt=f"{prompt}\nGive the most related word for this prompt, the word is used to acquire posts tagged by from tumrlr. web service:",
      temperature=0,
      max_tokens=20
    )

    # Extract the generated tags from the response
    tags = response.choices[0].text.strip().split(', ')

    return tags

def extract_post_data(post):
    # Extract the necessary fields from the post
    post_id = post['id']
    blog_name = post['blog_name']
    post_url = post['post_url']
    timestamp = post['timestamp']
    tags = post['tags']
    type = post['type']
    short_url = post['short_url']  # Add this line
    summary = post['summary']  # Add this line
    
    # Depending on the post type, extract the content differently
    if 'is_blocks_post_format' in post and post['is_blocks_post_format']:
        # NPF post
        content = post['content']
        layout = post['layout']
        trail = post['trail']
    else:
        # Legacy Text Post
        title = post.get('title', '')
        body = post.get('body', '')
        content = title + '\n' + body
    
    return {
        'id': post_id,
        'blog_name': blog_name,
        'url': post_url,
        'timestamp': timestamp,
        'tags': tags,
        'type': type,
        'content': content,
        'short_url': short_url,  # Add this line
        'summary': summary,  # Add this line
    }

'''
# the below function is trying to evaluate the relavant among posts to select the best one by GPT.

def select_post(prompt, posts_data):
    # Initialize a dictionary to hold post scores
    post_scores = {}

    # For each post, ask GPT-3 to score its relevance to the prompt
    for post in posts_data:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{prompt}\n{post['content']}\nScore this Tumblr post from 1 to 10:",
            temperature=0.5,
            max_tokens=3
        )

        # The score is the last line of the response
        score = int(response.choices[0].text.strip())

        # Store the score in the dictionary
        post_scores[post['id']] = score

    # Find the post with the highest score
    highest_scoring_post_id = max(post_scores, key=post_scores.get)
    highest_scoring_post = next(post for post in posts_data if post['id'] == highest_scoring_post_id)

    return highest_scoring_post
'''
def select_post(posts_data):
    # Sort the posts by timestamp (newest first)
    sorted_posts = sorted(posts_data, key=lambda k: k['timestamp'], reverse=True)
    
    # Select the newest post
    selected_post = sorted_posts[0]

    return selected_post
