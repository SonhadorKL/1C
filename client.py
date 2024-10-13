import socket
import json

class Client:
    def __init__(self, ip, port) -> None:
        """
        Принимает ip и port сервера для подключения к ученым,
        которые организую эксперимент
        """
        self.ip = ip
        self.port = port        


    def __connect_to_server(self):
        """
        Подключается к серверу.
        Оповещает пользователя, если connect был неуспешен.
        """
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client_socket.connect((server_ip, server_port))
        except:
            print("Такого сервера не существует")
            return False
        
        print("Подключение к серверу...")
        data = self.client_socket.recv(1024).decode('utf-8')
        message = json.loads(data)

        if message.get("error") != None:
            print(message["error"])
            return False
        if message.get('approve') != None:
            print(message['approve'])
        return True


    def __run_experiment(self):
        """
        Запускает одну партию эксперимента
        """
        print("Эксперимент начался!\nВам предстоит угадать число от 1 до 100.\nНа каждый ваш ответ вы будете узнавать, ваше число больше/меньше заданного")
        history = []
        while True:
            guess = input("Введите ваше предположение (число) или history, чтобы посмотреть историю ответов: ")
            if guess == 'history':
                print("История ваших предположений: ", history)
                continue
            
            if not guess.isalnum():
                continue
            
            self.client_socket.send(json.dumps({"action": "guess", "number": guess}).encode('utf-8'))

            response = json.loads(self.client_socket.recv(1024).decode('utf-8'))
            history.append(guess)

            if response['result'] == "correct":
                print("Вы угадали!")
                break
            elif response['result'] == "greater":
                print("Загаданное число больше")
            elif response['result'] == "lesser":
                print("Загаданное число меньше")
        print("Ожидайте следующих указаний от ученых")


    def __close_connection(self):
        self.client_socket.close()
        print("Эксперимент завершился")


    def run(self):
        """
        Подключается к серверу и обрабатывет его запросы
        """
        if not self.__connect_to_server():
            return
        while True:
            data = self.client_socket.recv(1024).decode('utf-8')
            message = json.loads(data)
            if message.get('action') != None and message['action'] == 'start':
                self.__run_experiment()

            if message.get('action') != None and message['action'] == 'stop':
                self.__close_connection()
                break

if __name__ == "__main__":
    server_ip = input("Введите IP сервера: ")
    server_port = 5555
    
    client = Client(server_ip, server_port)
    client.run()