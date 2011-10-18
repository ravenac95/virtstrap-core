from ConfigParser import ConfigParser

def main():
    config = ConfigParser()
    config.read('app.cfg')
    return config
