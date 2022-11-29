import gym
from gym import spaces
from gym.utils import seeding

def cmp(a, b):
    """
    Define la recompensa:
    Dadas dos puntuaciones, devuelve 1 si la primera es mayor que
    la segunda, -1 si la segunda es mayor que la primera y 0 si son
    iguales.
    """
    return int((a > b)) - int((a < b))

# 1 = Ace, 2-10 = Number cards, Jack/Queen/King = 10
deck = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]


def draw_card(np_random):
    """
    Reparte una carta:
    Devuelve un valor aleatorio de la baraja.
    """
    return np_random.choice(deck)


def draw_hand(np_random):
    """
    Reparte una mano:
    Devuelve dos cartas.
    """
    return [draw_card(np_random), draw_card(np_random)]


def usable_ace(hand):
    """
    Indica si una mano contiene un usable ace:
    Dada una mano, devuelve true si hay un ace y, otorgándole valor 11,
    la suma no excede 21; false en caso contrario.
    """   
    return 1 in hand and sum(hand) + 10 <= 21


def sum_hand(hand):
    """
    Dada una mano, devuelve su suma según las reglas del
    Blackjack (teniendo en cuenta si hay usable ace o no).
    """
    if usable_ace(hand):
            return sum(hand) + 10
    return sum(hand)


def is_bust(hand):
    """
    Indica si una mano se ha pasado:
    Dada una mano, devuelve 1 si suma más de 21 o 0 en caso contrario.
    """
    return sum_hand(hand) > 21


def score(hand): 
    """
    Calcula la puntuación de una mano:
    Dada una mano, devuelve 0 si se ha pasado de 21 o la suma de ésta
    si no se ha pasado. Rango: [0, 21].
    """
    return 0 if is_bust(hand) else sum_hand(hand)


class BlackjackEnv(gym.Env):
    """
    Entorno que inicializa y desarrolla un paso en el juego.
    """
    def __init__(self):
        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Tuple((
            spaces.Discrete(32),
            spaces.Discrete(11),
            spaces.Discrete(2)))
        self._seed()
        self._reset()

    def reset(self):
        return self._reset()

    def step(self, action):
        return self._step(action)

    def _seed(self, seed=None):
        """
        Establece una semilla para generar los números aleatorios
        utilizando la función de la librería gym.utils.
        """
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def _step(self, action):
        """
        Ejecuta un estado en función de la acción elegida:
        Si el jugador pide carta, se le reparte;
        si no, se reparte carta al dealer hasta sumar mínimo 17.
        Devuelve la observación; la recompensa -1 si el jugador se
        pasa o el dealer suma más, 1 si el jugador suma más que
        el dealer y 0 si suman lo mismo sin pasarse; y un booleano
        indicando si la partida ha finalizado.
        """
        assert self.action_space.contains(action), "Fallo, Action = {}".format(action)
        if action:  # Si la acción es 'pedir', se le reparte una carta al jugador y se calcula si finaliza o no el juego.
            self.player.append(draw_card(self.np_random))
            if is_bust(self.player):
                done = True
                reward = -1
            else:
                done = False
                reward = 0
        else:  # Si la acción es 'pasar', se le reparten cartas al dealer hasta que sume 17 o más, se calcula la recompensa y finaliza.
            done = True
            while sum_hand(self.dealer) < 17:
                self.dealer.append(draw_card(self.np_random))
            reward = cmp(score(self.player), score(self.dealer))
        return self._get_obs(), reward, done, {}

    def _get_obs(self):
        """
        Devuelve la suma de las cartas del jugador, la carta del dealer y
        un booleano indicando si el jugador contaba con un usable ace o no.
        """
        return (sum_hand(self.player), self.dealer[0], usable_ace(self.player))

    def _reset(self):
        """
        Reparte cartas al jugador (hasta que la suma de éstas sea mayor o 
        igual a 12) y al dealer. Devuelve la observación.
        """
        self.dealer = draw_hand(self.np_random)
        self.player = draw_hand(self.np_random)
        
        while sum_hand(self.player) < 12:
            self.player.append(draw_card(self.np_random))

        return self._get_obs()