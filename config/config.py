from environ import Env

env = Env()

STATE_TOPIC = env.str("STATE_TOPIC", "/bluetooth/audio")
LIST_TOPIC = env.str("LIST_TOPIC", "/bluetooth/list_songs")
QUERY_TOPIC = env.str("QUERY_TOPIC", "/bluetooth/ping")
SETTING_TOPIC = env.str("SETTING_TOPIC", "/bluetooth/config")

BROKER = env.str("BROKER", "192.168.1.2")
PORT = env.int("PORT", 1883)

DATABASE = env.str("DATABASE", "db.pkl")
