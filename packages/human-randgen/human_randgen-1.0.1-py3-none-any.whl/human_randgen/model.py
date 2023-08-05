import numpy as np

class HumanRng:
    # normal-inverse-gamma params
    u: float
    v: float
    a: float
    b: float

    def __newton(self, mode, var, max_itr = 16):
        """Calculates mean and variance of normal given mode and variance of lognormal."""
        b = np.log(var) - 2*np.log(mode)
        f = lambda s: np.log(np.exp(s) - 1) + 3*s - b
        g = lambda s: np.exp(s) / (np.exp(s) - 1) + 3

        v = 1
        for _ in range(max_itr):
            update = v - f(v) / g(v)
            update = max(update, 1e-5)

            diff = np.abs(update - v)

            v = update
            if diff < 1e-8:
                break

        u = np.log(mode) + v
        return u, v

    def __init__(self, mode = 1, sigma = 1, seed = None):
        if seed is not None:
            self.rng = np.random.default_rng(seed=seed)
        else:
            self.rng = np.random.default_rng()

        mean, var = self.__newton(mode, sigma**2)

        self.u = mean
        self.v = 1
        self.a = 1 
        self.b = var * (self.a + 1.5)

    def rand(self, num_samples = 1):
        mean, sigma = self.__map()
        if num_samples == 1:
            return self.rng.lognormal(mean, sigma)
        else:
            return self.rng.lognormal(mean, sigma, num_samples)

    def fit(self, xs):
        if len(xs) == 0:
            return

        data = np.log(np.array(xs))
        self.__update_posterior(data)

        mean, sigma = self.__map()

        mode = np.exp(mean - sigma**2)
        var = (np.exp(sigma**2) - 1) * np.exp(2*mean + sigma**2)

        print(f'Updated mode, sigma: {mode}, {np.sqrt(var)}')

    def __update_posterior(self, xs):
        sample_mean = np.average(xs)
        centered = xs - sample_mean
        n = xs.size

        u_n = (self.v*self.u + n*sample_mean) / (self.v + n)
        v_n = self.v + n
        a_n = self.a + n/2
        b_n = self.b + np.dot(centered, centered)/2 + n*self.v*(sample_mean-self.u)**2 / (self.v + n) / 2

        self.u, self.v, self.a, self.b = u_n, v_n, a_n, b_n

    def __map(self):
        return self.u, np.sqrt(self.b / (self.a + 1.5))
