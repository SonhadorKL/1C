import socket
import threading
import random
import json


class Server:
    def __init__(self) -> None:
        self.clients = {}
        self.leaderboard = {}
        self.active_users = 0
        self.number_to_guess = 0
        self.experiment_active = False
        self.server_running = False

    def start_experiment(self):
        """
        Загадывает случайное число и посылает сигнал пользователям о начале игры
        """
        for client in self.clients.values():
            client['attempts'] = 0
        self.number_to_guess = random.randint(1, 100)
        print("Эксперимент начался! Загаданное число:", self.number_to_guess)
        self.experiment_active = True
        self.active_users = len(self.clients)

        for client in self.clients.values():
            client['socket'].send(json.dumps({"action": "start"}).encode('utf-8'))
    
    def wait_clients(self):
        """
        Цикл ожидания подключений от новых пользователей
        """
        while self.server_running:
            try:  
                client_socket, addr = self.server.accept()
                client_handler = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                client_handler.start()
            except socket.error:
                continue

    def handle_client(self, client_socket, addr):
        """
        Метод, обрабатывающий взаимодействие с пользователем
        """
        client_id = addr[1]
        # Если эксперимент начался, то больше никого не впускаем
        if self.experiment_active:
            client_socket.send(json.dumps({"error": "Эксперимент уже начался, подключение невозможно."}).encode('utf-8'))
            client_socket.close()
            return

        # Успешно подключенный участник
        self.clients[client_id] = {"socket": client_socket, "attempts": 0, "history": []}
        client_socket.send(json.dumps({"approve" : "Успешное подключение"}).encode('utf-8'))
        print(f"Участник {client_id} подключился")
        while True:
            try:
                data = client_socket.recv(1024).decode('utf-8')
                message = json.loads(data)
                # Обработка предположения игрока
                if message['action'] == 'guess':
                    guess = int(message['number'])
                    self.clients[client_id]['attempts'] += 1
                    self.clients[client_id]['history'].append(guess)
                    if guess == self.number_to_guess:
                        response = {"result": "correct"}
                        client_socket.send(json.dumps(response).encode('utf-8'))
                        
                        if client_id in self.leaderboard:
                            self.leaderboard[client_id] += self.clients[client_id]['attempts']
                        else:
                            self.leaderboard[client_id] = self.clients[client_id]['attempts']

                        self.active_users -= 1
                        print(f"Участник {client_id} правильно угадал. Осталось {self.active_users} участников")
                    elif guess < self.number_to_guess:
                        response = {"result": "greater"}
                        client_socket.send(json.dumps(response).encode('utf-8'))
                    else:
                        response = {"result": "lesser"}
                        client_socket.send(json.dumps(response).encode('utf-8'))
            except:
                print(f"Участник {client_id} отключился")
                self.active_users -= 1
                break
        client_socket.close()
        del self.clients[client_id]


    def close_connection(self):
        self.server_running = False
        for client in self.clients.values():
            client['socket'].send(json.dumps({"action" : "stop"}).encode('utf-8'))
            client['socket'].close()
        self.server.close()


    def run(self):
        """
        Основной метод, реализующий взаимодействие с клиентами
        """
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', 5555))
        self.server.listen()
        self.server.setblocking(0)
        print("Сервер запущен, ожидание подключений...")
        self.server_running = True
        wait_threat = threading.Thread(target=self.wait_clients)
        wait_threat.start()
        print("Введите любое значение чтобы начать эксперимент")
        input()
        if len(self.clients) == 0:
            print("Никто не захотел играть в вашу игру. Закрываем сервер")
            self.close_connection()
            return
        
        print(f"Подключилось {len(self.clients)} человек")
        self.experiment_active = True
        while True:
            command = input("Введите команду (start/leaderboard/clients/exit): ")
            if command == "start":
                self.start_experiment()
                print(f"Ожидаем ответы от участников: {self.active_users}")
                while self.active_users != 0:
                    pass
            elif command == "leaderboard":
                print("Таблица лидеров:")
                for key in self.leaderboard.keys():
                    print(f"Участник {key} - {self.leaderboard[key]} попыток")
            elif command == "clients":
                print("Список участников:")
                for client_id in self.clients.keys():
                    print(f"Участник {client_id}")
            elif command == "exit":
                break
        self.close_connection()


if __name__ == "__main__":
    server = Server()
    server.run()
