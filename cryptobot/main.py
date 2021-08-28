import bittrex_websocket
import global_var

CONFIG_FILE = 'config.txt'


def load_api_keys():
    file = open(CONFIG_FILE, 'r')
    for line in file:
        elements = line.split()
        if elements[0] == 'API_KEY':
            global_var.api_key = elements[2]
        if elements[0] == 'API_SECRET':
            global_var.api_secret = elements[2]
    file.close()


def main():
    try:
        load_api_keys()
    except IOError:
        print('config file cannot be open')
    while True:
        try:
            bittrex_websocket.run()
        except Exception as err:
            print(f'Some error occurred:\n{err}\n')


if __name__ == '__main__':
    main()
