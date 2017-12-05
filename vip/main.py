import server

from config import CONFIG
CONFIG.parse()

if __name__ == '__main__':
	server.start()