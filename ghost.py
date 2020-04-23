import requests
import jwt
from datetime import datetime as date
import pytz
import json
import argparse
import keyboard

# Split the key into ID and SECRET
id, secret = key.split(':')

# Prepare header and payload
iat = int(date.now().timestamp())

# Create the token (including decoding secret)
header = {'alg': 'HS256', 'typ': 'JWT', 'kid': id}
payload = {
    'iat': iat,
    'exp': iat + 5 * 60,
    'aud': '/v3/admin/'
}
token = jwt.encode(payload, bytes.fromhex(secret), algorithm='HS256', headers=header)

# Ghost Information
# https://ghost.org/docs/api/v3/admin/
key = ''
url = ''
baseURL = url + 'ghost/api/v3/admin/'
postURL = baseURL + 'posts/'

# Variables
headers = {'Authorization': 'Ghost {}'.format(token.decode())}
description = "Create Ghost Blog Posts with Python"

# Date Time Variables
utc_time = date.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
rightNow = date.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
monthDay = date.now().strftime("%B %d")
timeStamp = date.now().strftime("%H:%M")

def timeConvert(convertedTime):
	# ISO 8601 	
	convertedTime = date.strptime(convertedTime, "%Y-%m-%d %H:%M")	
	local = pytz.timezone ("America/Chicago")
	local_dt = local.localize (convertedTime)
	utc_dt = local_dt.astimezone (pytz.utc)
	convertedTime = utc_dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")	
	return convertedTime

def deletePost(id):
	url = postURL + id
	content = requests.delete(url, headers=headers)
	print(url)

def createPost(html):
	body = {
		'posts': [{
			'title': monthDay,
			'status': "published",
			'html': timeStamp + '<br><br>' + html,
			'published_at': utc_time
		}]
	}
	content = requests.post(postURL + '?source=html', json=body, headers=headers)	
	content = json.loads(content.content.decode('utf-8'))
	print(content['posts'][0]['status'])

def importPost(title, published, html, publishedDate):
	body = {
		'posts': [{
			'title': title,
			'status': published,
			'html': html,
			'published_at': publishedDate
		}]
	}
	content = requests.post(postURL + '?source=html', json=body, headers=headers)
	return(content)

def getPosts():
	r = requests.get(postURL, headers=headers)
	content = json.loads(r.content.decode('utf-8'))
	for key, info in enumerate(content['posts']):
		for k, v in info.items():
			if k == "id" or k == "title":
				print('{0}:{1}'.format(k, v))				

def deleteAll():
	r = requests.get(postURL, headers=headers)
	content = json.loads(r.content.decode('utf-8'))
	for key, info in enumerate(content['posts']):
		for k, v in info.items():
			if k == "id":				
				deletePost(v)

parser = argparse.ArgumentParser(description=description, formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-g", "--get", action='store_true', help="Get Droplets")
parser.add_argument("-c", "--create", nargs= '*', help="Create Droplet")
parser.add_argument("--content", action='store_true', help="Create Droplet")
parser.add_argument("-d", "--delete", nargs= '*' , help="Delete Droplet")
parser.add_argument("-bd", "--bulkdelete", nargs= '*' , help="Delete Droplet")
parser.add_argument("--deleteAll", action='store_true' , help="Delete Droplet")
args = parser.parse_args()

if args.get:
    getPosts()
elif args.create:
	for content in args.create:
		createPost(content)
elif args.delete:
    for id in args.delete:
        deletePost(id)
elif args.deleteAll:
	print('Are you sure? (Y/N)')
	while True:
		if keyboard.read_key() == "y":
			print("Deleting All")
			deleteAll()
			break
		else:
			print("Cannceled")
			break
else:
	print('Empty Input')


