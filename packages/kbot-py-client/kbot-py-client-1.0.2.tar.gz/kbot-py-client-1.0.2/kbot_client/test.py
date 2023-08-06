
import json

from kbot_client import Client

client = Client("kjira.konverso.ai")
client.login("monitor", "kjdSDF23%sdf*")

metrics = client.metric()
print("Collected metrics (%s):" % (metrics))
print(metrics.text)
print(json.dumps(metrics.json(), indent=4))

r = client.conversation(username='bot')
print("Post conversation (%s):" % (r))
print(r.text)

r = client.get_dashboard(1)
print("Get dashboard (%s):" % (r))
print(r.text)

client.logout()
