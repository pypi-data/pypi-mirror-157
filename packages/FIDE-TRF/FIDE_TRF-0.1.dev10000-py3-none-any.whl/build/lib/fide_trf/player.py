from datetime import datetime


class Player:

    def __init__(self, raw_string=None):
        self.full_name = raw_string[10:43]
        self.starting_rank = raw_string[0:4]

        self.title = raw_string[6:9]
        self.gender = raw_string[5]

        self.fide_rating = raw_string[44:48]
        self.fide_federation = raw_string[49:52]
        self.fide_number = raw_string[53:64]

        self.birth_date = raw_string[65:75]
        self.rank = self.starting_rank

        self.rounds = raw_string[87:]

    @property
    def full_name(self):
        try:
            return f'{self.last_name}, {self.first_name}'
        except AttributeError:
            return self._full_name

    @full_name.setter
    def full_name(self, raw_string):
        full_name = raw_string.strip()
        try:
            self.last_name, self.first_name = full_name.split(', ')
        except ValueError:
            self._full_name = full_name

    @property
    def starting_rank(self):
        return self._starting_rank

    @starting_rank.setter
    def starting_rank(self, raw_string):
        self._starting_rank = int(raw_string)

    @property
    def fide_rating(self):
        return self._fide_rating

    @fide_rating.setter
    def fide_rating(self, raw_string):
        self._fide_rating = int(raw_string)

    @property
    def fide_number(self):
        return self._fide_number

    @fide_number.setter
    def fide_number(self, raw_string):
        self._fide_number = int(raw_string)

    @property
    def birth_date(self):
        return self._birth_date

    @birth_date.setter
    def birth_date(self, raw_string):
        try:
            self._birth_date = datetime.strptime(raw_string, '%Y/%m/%d')
        except ValueError:
            self._birth_date = ''

    @property
    def score(self):
        return sum(round_.result_points for round_ in self.rounds)

    @property
    def rounds(self):
        return self._rounds

    @rounds.setter
    def rounds(self, raw_string):
        self._rounds = [PlayerRound(raw_string[i:i+8])
                        for i in range(0, len(raw_string), 10)]

    def update_rank(self, new_rank):
        self.rank = new_rank

    def __str__(self):
        date_fmt = '%Y-%m-%d' if self.birth_date else '>10'
        return (f'{self.starting_rank:>4} {self.gender:>1}{self.title:>3} '
                f'{self.full_name:<33} '
                f'{self.fide_rating:>4} {self.fide_federation:>3} '
                f'{self.fide_number:>11} {self.birth_date:{date_fmt}} '
                f'{self.score:4.1f} {self.rank:>4}  '
                ) + '  '.join([f'{r}' for r in self.rounds])

    def __repr__(self):
        return (f'{self.__class__.__name__}(name={self.full_name!r}, '
                f'rating={self.fide_rating!r}, '
                f'fed={self.fide_federation!r}, score={self.score!r})')


class PlayerRound:
    points_table = {'=': 0.5, 1: 1, 0: 0,
                    'H': 0.5, 'F': 1, 'U': 1, 'Z': 0, ' ': 0,
                    '-': 0, '+': 1,
                    'W': 1, 'D': 0.5, 'L': 0}

    def __init__(self, raw_string):
        self.opponent_starting_rank = raw_string[:4]
        self.color = raw_string[5:6]
        self.result = raw_string[7:]

    @property
    def opponent_starting_rank(self):
        return self._opponent_starting_rank

    @opponent_starting_rank.setter
    def opponent_starting_rank(self, starting_rank_str):
        self._opponent_starting_rank = int(starting_rank_str)

    @property
    def result_points(self):
        return self.points_table[self.result]

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result_str):
        try:
            self._result = int(result_str)
        except ValueError:
            self._result = result_str.upper()

    def __str__(self):
        fill_char = 0 if self.opponent_starting_rank == 0 else ''
        return (f'{self.opponent_starting_rank:{fill_char}>4} '
                f'{self.color} {self.result}')

    def __repr__(self):
        return (f'{self.__class__.__name__}('
                f'opponentID={self.opponent_starting_rank!r}, '
                f'color={self.color!r}, result={self.result!r})')
