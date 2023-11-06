class Dot:
    def __init__(self, x, y):
        self.x = x    # Координата по оси x
        self.y = y    # Координата по оси y

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
    def __init__(self, hid, size=6):
        self.size = size
        self.hid = hid
        self.field = [["O"] * size for i in range(size)]
        self.list_of_ships = []
        self.occupied = []


    def out(self, dot):
        if dot.x < 1 or dot.y < 1 or dot.x > 6 or dot.y > 6:
            return True
        return False


    def add_ship(self, ship):
        for dot in ship.dots:
            if dot in self.occupied and dot in self.out(dot):
                raise WrongShipError()  # ДОПИСАТЬ ИСКЛЮЧЕНИЕ
        for dot in ship.dots:
            self.field[dot.x][dot.y] = "■"
            self.occupied.append(dot)

        self.list_of_ships.append(ship)

    def contour(self, ship):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for dot in ship.dots:
            for dx, dy in near:
                contour = Dot(dot.x + dx, dot.y + dy)
                if not(self.out(contour)) and contour not in self.occupied:
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
            raise ShotOutError() # ДОПИСАТЬ ИСКЛЮЧЕНИЕ

        if dot in self.occupied:
            raise ShotToUsedDot() # ДОПИСАТЬ ИСКЛЮЧЕНИЕ

        self.occupied.append(dot)

        for ship in self.list_of_ships:
            if dot in ship.dots:
                ship.hp -= 1
                self.field[dot.x][dot.y] = "X"
                if ship.hp == 0:
                    self.list_of_ships.pop(ship)
                    self.contour(ship)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[dot.x][dot.y] = "."
        print("Мимо!")
        return False

