from random import randint
class BoardException(Exception):
    pass

class ShotOutError(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы доски!"

class ShotToUsedDot(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"

class WrongShipError(BoardException):
    pass
class Dot:
    def __init__(self, x, y):
        self.x = x - 1   # Координата по оси x
        self.y = y - 1  # Координата по оси y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

class Ship:
    def __init__(self, length, bow, direction):
        self.length = length
        self.bow = bow
        self.direction = direction
        self.hp = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            if self.direction == 0:  # 0 - горизонтальное, 1 - вертикальное
                ship_coord = Dot(self.bow.x + i, self.bow.y)
            else:
                ship_coord = Dot(self.bow.x, self.bow.y + i)
            ship_dots.append(ship_coord)
        return ship_dots

class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.field = [["O"] * size for i in range(size)]
        self.list_of_ships = []
        self.occupied = []


    def out(self, dot):
        return not((0 <= dot.x < self.size) and (0 <= dot.y < self.size))


    def add_ship(self, ship):
        for dot in ship.dots:
            if self.out(dot) or dot in self.occupied:
                raise WrongShipError()

        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.occupied.append(dot)

        self.list_of_ships.append(ship)
        self.contour(ship)

    def contour(self, ship, ship_destroyed = False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.dots:
            for dx, dy in near:
                contour = Dot(dot.x + dx, dot.y + dy)
                if not(self.out(contour)) and contour not in self.occupied:
                    if ship_destroyed:
                        self.field[contour.x][contour.y] = "T"
                    self.occupied.append(contour)

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def shot(self, dot):
        if self.out(dot):
            raise ShotOutError()

        if dot in self.occupied:
            raise ShotToUsedDot()

        self.occupied.append(dot)

        for ship in self.list_of_ships:
            if dot in ship.dots:
                ship.hp -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.hp == 0:
                    self.list_of_ships.remove(ship)
                    self.contour(ship)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[dot.x][dot.y] = "T"
        print("Мимо!")
        return False

    def begin(self):
        self.occupied = [] #Обнуляем список занятых клеток после вызова игры

class Player:
    def __init__(self, board, enemy_board):
        self.board = board
        self.enemy_board = enemy_board

    def ask(self):
        raise NotImplementedError("будет использоваться в классах-наследниках")

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy_board.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        dot = Dot(randint(0, 5), randint(0, 5))
        print(f"Компьютер выстрелил в клетку {dot.x + 1},{dot.y + 1}")
        return dot


class User(Player):
    def ask(self):
        while True:
            coords = input("Введите координаты (напр., 2,3):").split()

            if len(coords) != 2:
                print("Введите 2 координаты!")
                continue

            x, y = coords

            if not (x.isdigit()) or not (y.isdigit()):
                print("Вводите числа!")
                continue

            x, y = int(x), int(y)

            return Dot(x, y)


class Game:
    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True

        self.ai = AI(computer, player)
        self.user = User(player, computer)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for length in [3, 2, 2, 1, 1, 1, 1]:
            while True:
                attempts += 1
                if attempts > 1000:
                    return None
                ship = Ship(length, Dot(randint(0, 5), randint(0, 5)), randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except WrongShipError:
                    pass
        board.begin()
        return board

    def greet(self):
        print('Добро пожаловать в игру "Морской бой"!')
        print("Введите 2 координаты: x и y ")
        print("x - номер строки  ")
        print("y - номер столбца ")
        print("игрок и компьютер ходят по очереди. Если игрок или компьютер попадают по кораблю, он ходит еще раз.")
        print("если промах - ход передается другому игроку.")
        print("Побеждает тот, кто первый уничтожит все корабли противника!")

    def loop(self):
        num = 0
        while True:
            print("---------------------------")
            print("Доска игрока:")
            print(self.user.board)
            print("---------------------------")
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ход игрока:")
                repeat = self.user.move()
            else:
                print("---------------------------")
                print("Ход компьютера:")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.list_of_ships == []:
                print("---------------------------")
                print("Игрок победил!")
                break

            if self.user.board.list_of_ships == []:
                print("---------------------------")
                print("компьютер победил!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()
