import requests, json
from pprint import pprint

slug_files = open("slugs.json", 'a',encoding='utf-8')

url = "https://api.opensea.io/api/v1/collections"
run = True
slugs = []
i = 0
count = 0

while i < 167:
    try:
        querystring = {"offset": i*300, "limit": "300"}
        print(f"processing {i}")
        response = requests.request("GET", url, params=querystring)
        result = json.loads(response.text)

        for c in result["collections"]:
            slug = c["slug"]
            if slug not in slugs:
                slugs.append(slug)
            count += 1

    except Exception as e:
        print(f"ERROR: {e}")
        print(i)

    i += 1

print(f"\n {count} \n")

slug_files.seek(0)
slug_files.truncate()
json.dump(slugs, slug_files, indent=4)
slug_files.close()
