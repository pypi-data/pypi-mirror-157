class NumBase:
    
    def __init__(self, number: str, base: int):
        self.base = base
        self.number = number
        alphs = '0123456789ABCDEF'
        if self.base in range(2, 17):
            if "." not in number:
                is_minus = False
                if number[0] == '-':
                    is_minus = True
                    self.number = number[1:]
                    check = True
                    for i in self.number:
                        if i not in alphs[:base]:
                            check = False
                            raise TypeError("Wrong base")
                    if check:
                        self.number = number
                if number[0] != '-':
                    self.number = number
                    check = True
                    for i in self.number:
                        if i not in alphs[:base]:
                            check = False
                            raise TypeError("Wrong base")
                    if check:
                        self.number = number
            if "." in number:
                is_minus = False
                if number[0] == '-':
                    is_minus = True
                    self.number = ''.join(number.split('.'))[1:]
                    check = True
                    for i in self.number:
                        if i not in alphs[:base]:
                            check = False
                            raise TypeError("Wrong base")
                    if check:
                        self.number = number
                if number[0] != '-':
                    self.number = ''.join(number.split('.'))
                    check = True
                    for i in self.number:
                        if i not in alphs[:base]:
                            check = False
                            raise TypeError("Wrong base")
                    if check:
                        self.number = number
        else:
            raise TypeError("Wrong base")

    def __repr__(self):
        return self.number + ',' + ' ' + str(self.base)

    def to_decimal(number: str, base: int) -> str:
        if base in range(2, 17):
            alphs = '0123456789ABCDEF'
            rest = []
            if "." not in number:
                return int(number, base)
            if "." in number:
                first_number = int(number.split('.')[0], base)
                second_number = number.split('.')[1]
                for i in range(len(second_number)):
                    my_index = alphs.index(second_number[i])
                    rest.append(my_index * (base ** (-(i + 1))))
                rest = sum(rest)
                return float(str(first_number) + '.' + str(rest)[2:])
        else:
            raise TypeError("Wrong base")

    def from_decimal(number: int, base: int) -> str:
        if base in range(2, 17):
            rest = ''
            rest_1 = ''
            alphs = "0123456789ABCDEF"
            if isinstance(number, int):
                is_minus = False
                if number < 0:
                    is_minus = True
                    number = abs(number)
                while number != 0:
                    rest += alphs[number % base]
                    number //= base
                if is_minus:
                    return '-' + rest[::-1]
                return rest[::-1]
            if isinstance(number, float):
                is_minus = False
                if number < 0:
                    is_minus = True
                number = abs(number)
                first_number = int(number)
                while first_number != 0:
                    rest_1 += alphs[first_number % base]
                    first_number //= base
                second_number = round(number - int(number), 4)
                mul = second_number * base
                while len(str(rest)) <= 6:
                    rest += alphs[int(mul)]
                    mul = (mul - int(mul)) * base
                if first_number == 0:
                    return str(first_number) + '.' + rest
                if is_minus:
                    return '-' + rest_1[::-1] + '.' + rest
                return rest_1[::-1] + '.' + rest
        else:
            raise TypeError("Wrong base")

    def __add__(self, other):
        if self.base == other.base:
            first_dec_num = NumBase.to_decimal(self.number, self.base)
            second_dec_num = NumBase.to_decimal(other.number, other.base)
            return NumBase.from_decimal(first_dec_num + second_dec_num, self.base)
        else:
            raise TypeError("Different systems")

    def add(self, other, base):
        first_dec_num = NumBase.to_decimal(self.number, self.base)
        second_dec_num = NumBase.to_decimal(other.number, other.base)
        return NumBase.from_decimal(first_dec_num + second_dec_num, base)

    def __sub__(self, other):
        if self.base == other.base:
            first_dec_num = NumBase.to_decimal(self.number, self.base)
            second_dec_num = NumBase.to_decimal(other.number, other.base)
            return NumBase.from_decimal(first_dec_num - second_dec_num, self.base)
        else:
            raise TypeError("Different systems")

    def sub(self, other, base):
        first_dec_num = NumBase.to_decimal(self.number, self.base)
        second_dec_num = NumBase.to_decimal(other.number, other.base)
        return NumBase.from_decimal(first_dec_num - second_dec_num, base)

    def __mul__(self, other):
        if self.base == other.base:
            first_dec_num = NumBase.to_decimal(self.number, self.base)
            second_dec_num = NumBase.to_decimal(other.number, other.base)
            return NumBase.from_decimal(first_dec_num * second_dec_num, self.base)
        else:
            raise TypeError("Different systems")

    def mul(self, other, base):
        first_dec_num = NumBase.to_decimal(self.number, self.base)
        second_dec_num = NumBase.to_decimal(other.number, other.base)
        return NumBase.from_decimal(first_dec_num * second_dec_num, base)

    def __truediv__(self, other):
        if self.base == other.base:
            first_dec_num = NumBase.to_decimal(self.number, self.base)
            second_dec_num = NumBase.to_decimal(other.number, other.base)
            return NumBase.from_decimal(first_dec_num / second_dec_num, self.base)
        else:
            raise TypeError("Different systems")

    def truediv(self, other, base):
        first_dec_num = NumBase.to_decimal(self.number, self.base)
        second_dec_num = NumBase.to_decimal(other.number, other.base)
        return NumBase.from_decimal(first_dec_num / second_dec_num, base)

    def __pow__(self, other):
        if self.base == other.base:
            first_dec_num = NumBase.to_decimal(self.number, self.base)
            second_dec_num = NumBase.to_decimal(other.number, other.base)
            return NumBase.from_decimal(first_dec_num ** second_dec_num, self.base)
        else:
            raise TypeError("Different systems")

    def pow_(self, other, base):
        first_dec_num = NumBase.to_decimal(self.number, self.base)
        second_dec_num = NumBase.to_decimal(other.number, other.base)
        return NumBase.from_decimal(first_dec_num ** second_dec_num, base)

    def __mod__(self, other):
        if self.base == other.base:
            first_dec_num = NumBase.to_decimal(self.number, self.base)
            second_dec_num = NumBase.to_decimal(other.number, other.base)
            return NumBase.from_decimal(first_dec_num % second_dec_num, self.base)
        else:
            raise TypeError("Different systems")

    def mod(self, other, base):
        first_dec_num = NumBase.to_decimal(self.number, self.base)
        second_dec_num = NumBase.to_decimal(other.number, other.base)
        return NumBase.from_decimal(first_dec_num % second_dec_num, base)
