from math import sqrt, log, gcd
from random import randrange
from functools import reduce
from operator import mul
from time import time
from rsa import newkeys, encrypt, decrypt, PrivateKey
from rsa.common import inverse
from binascii import b2a_hex
from secrets import choice
from string import printable

PRIMES_31 = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31)
PRIMONIAL_31 = reduce(mul, PRIMES_31)

def lcm(a, b):
    return a // gcd(a, b) * b

class FactoredInteger():
    def __init__(self, integer, factors = None):
        self.integer = int(integer)
        if factors is None:
            self.factors = dict(_factor(self.integer)[0])

        else:
            self.factors = dict(factors)

    @classmethod
    def from_partial_factorization(cls, integer, partial):
        partial_factor = 1
        for p, e in partial.iteritems():
            partial_factor *= p ** e

        return cls(integer // partial_factor) * cls(partial_factor, partial)

    def __iter__(self):
        return self.factors.iteritems()

    def __mul__(self, other):
        if isinstance(other, FactoredInteger):
            integer = self.integer * other.integer
            new_factors = self.factors.copy()
            for p in other.factors:
                new_factors[p] = new_factors.get(p, 0) + other.factors[p]

            return self.__class__(integer, new_factors)

        else:
            return self * FactoredInteger(other)

    __rmul__ = __mul__

    def __pow__(self, other):
        new_integer = self.integer ** other
        new_factors = {}
        for p in self.factors:
            new_factors[p] = self.factors[p] * other

        return self.__class__(new_integer, new_factors)

    def __mod__(self, other):
        try:
            if other.integer in self.factors:
                return 0

            return self.integer % other.integer
            
        except AttributeError:
            if int(other) in self.factors:
                return 0

            return self.integer % int(other)

    def copy(self):
        return self.__class__(self.integer, self.factors.copy())

    def is_divisible_by(self, other):
        if int(other) in self.factors:
            return True

        return not self.integer % int(other)

    def exact_division(self, other):
        divisor = int(other)
        quotient = self.copy()
        if divisor in quotient.factors:
            if quotient.factors[divisor] == 1:
                del quotient.factors[divisor]

            else:
                quotient.factors[divisor] -= 1

        elif not isinstance(other, FactoredInteger):
            dividing = divisor
            for p, e in self.factors.iteritems():
                while not dividing % p:
                    dividing //= p
                    if quotient.factors[p] == 1:
                        del quotient.factors[p]
                        assert dividing % p, dividing

                    else:
                        quotient.factors[p] -= 1

                if dividing == 1:
                    break

            assert dividing == 1

        else:
            for p, e in other.factors.iteritems():
                assert p in quotient.factors and quotient.factors[p] >= e
                if quotient.factors[p] == e:
                    del quotient.factors[p]

                else:
                    quotient.factors[p] -= e

        quotient.integer //= divisor
        return quotient

    __floordiv__ = exact_division

    def divisors(self):
        divs = [FactoredInteger(1)]
        for p, e in self.factors.iteritems():
            q = FactoredInteger(1)
            pcoprimes = list(divs)
            for j in range(1, e + 1):
                q *= FactoredInteger(p, {p:1})
                divs += [k * q for k in pcoprimes]
        return divs

    def proper_divisors(self):
        return self.divisors()[1:-1]

    def prime_divisors(self):
        return self.factors.keys()

class TestPrime():
    primes = PRIMES_31
    primecache = set(primes)
    def __init__(self, t = 12):
        if isinstance(t, int):
            self.t = FactoredInteger(t)

        else:
            assert isinstance(t, FactoredInteger)
            self.t = t

        powerof2 = self.t.factors[2] + 2
        self.et = FactoredInteger(2 ** powerof2, {2:powerof2})
        for d in self.t.divisors():
            p = d.integer + 1
            if p & 1 and (p in self.primecache or is_prime(p, d.factors)):
                self.et = self.et * FactoredInteger(p, {p:1})
                if p in self.t.factors:
                    e = self.t.factors[p]
                    self.et = self.et * FactoredInteger(p ** e, {p:e})

                self.primecache.add(p)

    def next(self):
        eu = []
        for p in self.primes:
            if p in self.t.factors:
                eu.append((p - 1) * p ** (self.t.factors[p] - 1))
            else:
                eu.append(p - 1)
                break
        p = self.primes[eu.index(min(eu))]
        return self.__class__(self.t * FactoredInteger(p, {p:1}))

def primitive_root(p):
    pd = FactoredInteger(p - 1).proper_divisors()
    for i in range(2, p):
        for d in pd:
            if pow(i, (p - 1) // d, p) == 1:
                break

        else:
            return i

class Zeta():
    def __init__(self, size, pos = None, val = 1):
        self.size = size
        self.z = [0] * self.size
        if pos is not None:
            self.z[pos % self.size] = val

    def __add__(self, other):
        if self.size == other.size:
            m = self.size
            zr_a = Zeta(m)
            for i in range(m):
                zr_a.z[i] = self.z[i] + other.z[i]

            return zr_a

        else:
            m = lcm(self.size, other.size)
            return self.promote(m) + other.promote(m)

    def __mul__(self, other):
        if not isinstance(other, Zeta):
            zr_m = Zeta(self.size)
            zr_m.z = [x * other for x in self.z]
            return zr_m

        elif self.size == other.size:
            zr_m = Zeta(self.size)
            other = abs(other)
            for k in range(other.size):
                if not other.z[k]:
                    continue

                elif other.z[k] == 1:
                    zr_m = zr_m + (self << k)

                else:
                    zr_m = zr_m + (self << k) * other.z[k]

            return zr_m

        else:
            m = lcm(self.size, other.size)
            return self.promote(m) * other.promote(m)

    __rmul__ = __mul__

    def promote(self, size):
        if size == self.size:
            return abs(self)

        new = Zeta(size)
        r = size // self.size
        for i in range(self.size):
            new.z[i * r] = self.z[i]

        return new

    def weight(self):
        return len(filter(None, self.z))

    def mass(self):
        return sum(self.z)

def is_prime(n):
    if n in [2, 3, 5, 7]:
        return True

    if not (n % 10 % 2) or n % 10 not in [1, 3, 7, 9] or n <= 1 or not isinstance(n, int):
        return False

    if gcd(n, PRIMONIAL_31) > 1:
        return (n in PRIMES_31)

    if n < 999999999999999:
        for i in range(2, int(n ** 0.5 + 1)):
            if n % i == 0:
                return False

        return True

    if not smallSpsp(n):
        return False

    if n < 10 ** 12:
        return True
    
    return apr(n)

class Status():
    def __init__(self):
        self.d = {}

    def yet(self, key):
        self.d[key] = 0

    def done(self, key):
        self.d[key] = 1

    def yet_keys(self):
        return [k for k in self.d if not self.d[k]]

    def isDone(self, key):
        return self.d[key]

    def subodd(self, p, q, n, J):
        s = J.get(1, p, q)
        Jpq = J.get(1, p, q)
        m = s.size
        for x in range(2, m):
            if x % p == 0:
                continue

            sx = Zeta(m)
            i = x
            j = 1
            while i > 0:
                sx[j] = Jpq[i]
                i = (i + x) % m
                j += 1

            sx[0] = Jpq[0]
            sx = pow(sx, x, n)
            s = s * sx % n

        s = pow(s, n // m, n)
        r = n % m
        t = 1
        for x in range(1, m):
            if x % p == 0:
                continue

            c = (r * x) // m
            if c:
                tx = Zeta(m)
                i = x
                j = 1
                while i > 0:
                    tx[j] = Jpq[i]
                    i = (i + x) % m
                    j += 1

                tx[0] = Jpq[0]
                tx = pow(tx, c, n)
                t = t * tx % n

        s = abs(t * s % n)
        if s.weight() == 1 and s.mass() == 1:
            for i in range(1, m):
                if gcd(m, s.z.index(1)) == 1:
                    self.done(p)
                    
                return True

        return False

    def sub8(self, q, k, n, J):
        s = J.get(3, q)
        J3 = J.get(3, q)
        m = len(s)
        sx_z = {1:s}
        x = 3
        step = 2
        while m > x:
            z_4b = Zeta(m)
            i = x
            j = 1
            while i != 0:
                z_4b[j] = J3[i]
                i = (i + x) % m
                j += 1

            z_4b[0] = J3[0]
            sx_z[x] = z_4b
            s = pow(sx_z[x], x, n) * s
            step = 8 - step
            x += step

        s = pow(s, n // m, n)
        r = n % m
        step = 2
        x = 3
        while m > x:
            c = r*x
            if c > m:
                s = pow(sx_z[x], c // m, n) * s

            step = 8 - step
            x += step

        r = r & 7
        if r == 5 or r == 7:
            s = J.get(2, q).promote(m) * s

        s = abs(s % n)

        if s.weight() == 1 and s.mass() == 1:
            if gcd(m, s.z.index(1)) == 1 and pow(q, (n-1) >> 1, n) == n-1:
                self.done(2)

            return True

        elif s.weight() == 1 and s.mass() == n-1:
            if gcd(m, s.z.index(n-1)) == 1 and pow(q, (n-1) >> 1, n) == n-1:
                self.done(2)

            return True

        return False

    def sub4(self, q, n, J):
        j2 = J.get(1, 2, q) ** 2
        s = q * j2 % n
        s = pow(s, n >> 2, n)
        if n & 3 == 3:
            s = s * j2 % n
            
        s = abs(s % n)
        if s.weight() == 1 and s.mass() == 1:
            i = s.z.index(1)
            if (i == 1 or i == 3) and pow(q, (n-1) >> 1, n) == n-1:
                self.done(2)

            return True

        return False

    def sub2(self, q, n):
        s = pow(n - q, (n - 1) >> 1, n)
        if s == n-1:
            if n & 3 == 1:
                self.done(2)

        elif s != 1:
            return False

        return True

    def subrest(self, p, n, et, J, ub = 200):
        if p == 2:
            q = 5
            while q < 2 * ub + 5:
                q += 2
                if not is_prime(q) or et % q == 0:
                    continue

                if n % q == 0:
                    return False

                k = vp(q - 1, 2)[0]
                if k == 1:
                    if n & 3 == 1 and not self.sub2(q, n):
                        return False

                elif k == 2:
                    if not self.sub4(q, n, J):
                        return False

                else:
                    if not self.sub8(q, k, n, J):
                        return False

                if self.isDone(p):
                    return True

            else:
                return

        else:
            step = p * 2
            q = 1
            while q < step * ub + 1:
                q += step
                if not is_prime(q) or et % q == 0:
                    continue

                if n % q == 0:
                    return False

                if not self.subodd(p, q, n, J):
                    return False

                if self.isDone(p):
                    return True

            else:
                return

def _factor(n):
    def factor(n):
        if n % 2 == 0:
            return 2

        a = 2
        i = 2
        while True:
            a = pow(a, i, n)
            d = gcd(a - 1, n)
            if d > 1:
                return d

            i += 1

    num = n
    ans = []
    if is_prime(n):
        ans.append(n)
        return ans

    while True:
        d = factor(num)
        ans.append(d)
        r = num // d
        if is_prime(r):
            ans.append(r)
            break
    
        else:
            num = r
    
    ans.sort()
    result = list(set([(x, ans.count(x)) for x in ans]))
    return result, ans

class JacobiSum():
    def __init__(self):
        self.shelve = {}

    def get(self, group, p, q = None):
        if q:
            assert group == 1
            if (group, p, q) not in self.shelve:
                self.make(q)

            return self.shelve[group, p, q]

        else:
            assert group == 2 or group == 3
            if (group, p) not in self.shelve:
                self.make(p)

            return self.shelve[group, p]

    def make(self, q):
        fx = self.makefx(q)
        qpred = q - 1
        qt = _factor(qpred)[0]
        qt2 = [k for (p, k) in qt if p == 2][0]
        k, pk = qt2, 2 ** qt2
        if k >= 2:
            J2q = Zeta(pk, 1 + fx[1])
            for j in range(2, qpred):
                J2q[j + fx[j]] = J2q[j + fx[j]] + 1

            self.shelve[1, 2, q] = +J2q
            if k >= 3:
                J2 = Zeta(8, 3 + fx[1])
                J3 = Zeta(pk, 2 + fx[1])
                for j in range(2, qpred):
                    J2[j * 3 + fx[j]] = J2[j * 3 + fx[j]] + 1
                    J3[j * 2 + fx[j]] = J3[j * 2 + fx[j]] + 1

                self.shelve[3, q] = abs(self.shelve[1, 2, q] * J3)
                self.shelve[2, q] = abs(J2 ** 2)

        else:
            self.shelve[1, 2, q] = 1

        for (p, k) in qt:
            if p == 2:
                continue

            pk = p ** k
            Jpq = Zeta(pk, 1 + fx[1])
            for j in range(2, qpred):
                Jpq[j + fx[j]] = Jpq[j + fx[j]] + 1

            self.shelve[1, p, q] = +Jpq

    @staticmethod
    def makefx(q):
        g = primitive_root(q)
        qpred = q - 1
        qd2 = qpred >> 1
        g_mf = [0, g]
        for _ in range(2, qpred):
            g_mf.append((g_mf[-1] * g) % q)

        fx = {}
        for i in range(1, qd2):
            if i in fx:
                continue

            j = g_mf.index(q + 1 - g_mf[i])
            fx[i] = j
            fx[j] = i
            fx[qpred - i] = (j - i + qd2) % qpred
            fx[fx[qpred - i]] = qpred - i
            fx[qpred - j] = (i - j + qd2) % qpred
            fx[fx[qpred - j]] = qpred - j

        return fx

def apr(n):
    L = Status()
    rb = floorsqrt(n) + 1
    el = TestPrime()
    while el.et <= rb:
        el = el.next()

    plist = el.t.factors.keys()
    plist.remove(2)
    L.yet(2)
    for p in plist:
        if pow(n, p - 1, p ** 2) != 1:
            L.done(p)

        else:
            L.yet(p)

    qlist = el.et.factors.keys()
    qlist.remove(2)
    J = JacobiSum()
    for q in qlist:
        for p in plist:
            if (q - 1) % p != 0:
                continue

            if not L.subodd(p, q, n, J):
                return False

        k = vp(q - 1, 2)[0]
        if k == 1:
            if not L.sub2(q, n):
                return False

        elif k == 2:
            if not L.sub4(q, n, J):
                return False

        else:
            if not L.sub8(q, k, n, J):
                return False

    for p in L.yet_keys():
        if not L.subrest(p, n, el.et, J):
            return False

    r = int(n)
    for _ in range(1, el.t.integer):
        r = (r * n) % el.et.integer
        if n % r == 0 and r != 1 and r != n:
            return False

    return True

def spsp(n, base, s = None, t = None):
    if s is None or t is None:
        s, t = vp(n - 1, 2)

    z = pow(base, t, n)
    if z != 1 and z != n-1:
        j = 0
        while j < s:
            j += 1
            z = pow(z, 2, n)
            if z == n - 1:
                break

        else:
            return False

    return True

def smallSpsp(n, s = None, t = None):
    if s is None or t is None:
        s, t = vp(n - 1, 2)

    for p in (2, 13, 23, 1662803):
        if not spsp(n, p, s, t):
            return False

    return True

def extgcd(x, y):
    a, b, g, u, v, w = 1, 0, x, 0, 1, y
    while w:
        q, t = divmod(g, w)
        a, b, g, u, v, w = u, v, w, a - q * u, b - q * v, t

    if g >= 0:
        return (a, b, g)

    else:
        return (-a, -b, -g)

def legendre(a, m):
    a %= m
    symbol = 1
    while a != 0:
        while a & 1 == 0:
            a >>= 1
            if m & 7 == 3 or m & 7 == 5:
                symbol = -symbol

        a, m = m, a
        if a & 3 == 3 and m & 3 == 3:
            symbol = -symbol

        a %= m

    if m == 1:
        return symbol

    return 0

def inverse(x, n):
    x %=  n
    y = extgcd(n, x)
    if y[2] == 1:
        if y[1] < 0:
            r = n + y[1]
            return r

        else:
            return y[1]

def vp(n, p, k = 0):
    q = p
    while not (n % q):
        k += 1
        q *= p

    return (k, n // (q // p))

def modsqrt(n, p, e = 1):
    if 1 < e:
        x = modsqrt(n, p)
        if 0 == x:
            return

        ppower = p
        z = inverse(x << 1, p)
        for i in range(e - 1):
            x += (n - x ** 2) // ppower * z % p * ppower
            ppower *= p

        return x
    
    symbol = legendre(n, p)
    if symbol == 1:
        pmod8 = p & 7
        if pmod8 != 1:
            n %= p
            if pmod8 == 3 or pmod8 == 7:
                x = pow(n, (p >> 2) + 1, p)

            else:
                x = pow(n, (p >> 3) + 1, p)
                c = pow(x, 2, p)
                if c != n:
                    x = (x * pow(2, p >> 2, p)) % p

        else:
            d = 2
            while legendre(d, p) != -1:
                d = randrange(3, p)

            s, t = vp(p-1, 2)
            A = pow(n, t, p)
            D = pow(d, t, p)
            m = 0
            for i in range(1, s):
                if pow(A*(D**m), 1 << (s-1-i), p) == (p-1):
                    m += 1 << i

            x = (pow(n, (t+1) >> 1, p) * pow(D, m >> 1, p)) % p

        return x

    elif symbol == 0:
        return 0

    else:
        return

def floorsqrt(a):
    if a < (1 << 59):
        return int(sqrt(a))

    else:
        x = pow(10, (int(log(a, 10)) >> 1) + 1)
        while True:
            x_new = (x + a // x) >> 1
            if x <= x_new:
                return x

            x = x_new

class QS(object):
    def __init__(self, n, sieverange, factorbase):
        self.number = n
        self.sqrt_n = int(sqrt(n))
        for i in PRIMES_31:
            if n % i == 0:
                return n % 1

        self.digit = log(self.number, 10) + 1
        self.Srange = sieverange
        self.FBN = factorbase
        self.move_range = range(self.sqrt_n - self.Srange, self.sqrt_n + self.Srange + 1)
        i = 0
        k = 0
        factor_base = [-1]
        FB_log = [0]
        while True:
            ii = primes_table[i]
            if legendre(self.number, ii) == 1:
                factor_base.append(ii)
                FB_log.append(primes_log_table[i])
                k += 1
                i += 1
                if k == self.FBN:
                    break

            else:
                i += 1

        self.FB = factor_base
        self.FB_log = FB_log
        self.maxFB = factor_base[-1]
        N_sqrt_list = []
        for i in self.FB:
            if i != 2 and i != -1:
                e = int(log(2*self.Srange, i))
                N_sqrt_modp = sqroot_power(self.number, i, e)
                N_sqrt_list.append(N_sqrt_modp)

        self.solution = N_sqrt_list
        poly_table = []
        log_poly = []
        minus_val = []
        for j in self.move_range:
            jj = (j ** 2) - self.number
            if jj < 0:
                jj = -jj
                minus_val.append(j - self.sqrt_n + self.Srange)

            elif jj == 0:
                jj = 1

            lj = int((log(jj) * 30) * 0.97)
            poly_table.append(jj)
            log_poly.append(lj)
        self.poly_table = poly_table
        self.log_poly = log_poly
        self.minus_check = minus_val

    def run_sieve(self):
        M = self.Srange
        start_location = []
        logp = [0] * (2 * M + 1)
        j = 2
        for i in self.solution:
            k = 0
            start_p = []
            while k < len(i):
                q = int((self.sqrt_n) / (self.FB[j] ** (k + 1)))
                s_1 = q * (self.FB[j] ** (k + 1)) + i[k][0]
                s_2 = q * (self.FB[j] ** (k + 1)) + i[k][1]
                while True:
                    if s_1 < self.sqrt_n-M:
                        s_1 += (self.FB[j] ** (k + 1))
                        break

                    else:
                        s_1 -= (self.FB[j] ** (k + 1))

                while True:
                    if s_2 < self.sqrt_n-M:
                        s_2 += (self.FB[j] ** (k + 1))
                        break

                    else:
                        s_2 -= (self.FB[j] ** (k + 1))

                start_p.append([s_1 - self.sqrt_n + M, s_2 - self.sqrt_n + M])
                k += 1

            start_location.append(start_p)
            j += 1

        self.start_location = start_location
        if self.poly_table[0] & 1 == 0:
            i = 0
            while i <= 2 * M:
                j = 1
                while True:
                    if self.poly_table[i] % (2 ** (j + 1)) == 0:
                        j += 1

                    else:
                        break

                logp[i] += self.FB_log[1] * j
                i += 2

        else:
            i = 1
            while i <= 2 * M:
                j = 1
                while True:
                    if self.poly_table[i] % (2 ** (j + 1)) == 0:
                        j += 1

                    else:
                        break

                logp[i] += self.FB_log[1] * j
                i += 2

        L = 2
        for j in self.start_location:
            k = 0
            while k < len(j):
                s_1 = j[k][0]
                s_2 = j[k][1]
                h_1 = 0
                h_2 = 0
                while s_1 + h_1 <= 2 * M:
                    logp[s_1 + h_1] += self.FB_log[L]
                    h_1 += self.FB[L] ** (k + 1)

                while s_2 + h_2 <= 2 * M:
                    logp[s_2 + h_2] += self.FB_log[L]
                    h_2 += self.FB[L] ** (k + 1)

                k += 1

            L += 1

        self.logp = logp
        smooth = []
        for t in range(2 * M + 1):
            if logp[t] >= self.log_poly[t]:
                poly_val = self.poly_table[t]
                index_vector = []
                for p in self.FB:
                    if p == -1:
                        if t in self.minus_check:
                            index_vector.append(1)

                        else:
                            index_vector.append(0)

                    else:
                        r = 0
                        while poly_val % (p ** (r + 1)) == 0:
                            r += 1

                        v = r & 1
                        index_vector.append(v)

                smooth.append([index_vector, (poly_val, t + self.sqrt_n - M)])

        self.smooth = smooth
        return smooth

class MPQS(object):
    def __init__(self, n, sieverange = 0, factorbase = 0, multiplier = 0):
        self.number = n
        if is_prime(self.number):
            return [n]

        for i in PRIMES_31:
            if n % i == 0:
                return n % 1

        self.sievingtime = 0
        self.coefficienttime = 0
        self.d_list = []
        self.a_list = []
        self.b_list = []
        self.digit = int(log(self.number, 10) + 1)
        if sieverange != 0:
            self.Srange = sieverange
            if factorbase != 0:
                self.FBN = factorbase
            elif self.digit < 9:
                self.FBN = parameters_for_mpqs[0][1]
            else:
                self.FBN = parameters_for_mpqs[self.digit - 9][1]

        elif factorbase != 0:
            self.FBN = factorbase
            if self.digit < 9:
                self.Srange = parameters_for_mpqs[0][0]
            else:
                self.Srange = parameters_for_mpqs[self.digit - 9][0]

        elif self.digit < 9:
            self.Srange = parameters_for_mpqs[0][0]
            self.FBN = parameters_for_mpqs[0][1]

        elif self.digit > 53:
            self.Srange = parameters_for_mpqs[44][0]
            self.FBN = parameters_for_mpqs[44][1]

        else:
            self.Srange = parameters_for_mpqs[self.digit - 9][0]
            self.FBN = parameters_for_mpqs[self.digit - 9][1]

        self.move_range = range(-self.Srange, self.Srange + 1)
        if multiplier == 0:
            self.sqrt_state = []
            for i in [3, 5, 7, 11, 13]:
                s = legendre(self.number, i)
                self.sqrt_state.append(s)

            if self.number % 8 == 1 and self.sqrt_state == [1, 1, 1, 1, 1]:
                k = 1

            else:
                index8 = (self.number & 7) >> 1
                j = 0
                while self.sqrt_state != prime_8[index8][j][1]:
                    j += 1

                k = prime_8[index8][j][0]
        else:
            if n & 3 == 1:
                k = 1

            else:
                if multiplier == 1:
                    return n

                else:
                    k = multiplier

        self.number = k * self.number
        self.multiplier = k
        i = 0
        k = 0
        factor_base = [-1]
        FB_log = [0]
        while k < self.FBN:
            ii = primes_table[i]
            if legendre(self.number,ii) == 1:
                factor_base.append(ii)
                FB_log.append(primes_log_table[i])
                k += 1

            i += 1

        self.FB = factor_base
        self.FB_log = FB_log
        self.maxFB = factor_base[-1]
        N_sqrt_list = []
        for i in self.FB:
            if i != 2 and i != -1:
                e = int(log(2 * self.Srange, i))
                N_sqrt_modp = sqroot_power(self.number, i, e)
                N_sqrt_list.append(N_sqrt_modp)

        self.Nsqrt = N_sqrt_list

    def make_poly(self):
        if self.d_list == []:
            d = int(sqrt((sqrt(self.number) / (sqrt(2) * self.Srange))))
            if d & 1 == 0:
                if (d + 1)& 3 == 1:
                    d += 3

                else:
                    d += 1

            elif d & 3 == 1:
                d += 2

        else:
            d = self.d_list[-1]

        while d in self.d_list or not is_prime(d) or legendre(self.number, d) != 1 or d in self.FB:
            d += 4

        a = d ** 2
        h_0 = pow(self.number, (d - 3) >> 2, d)
        h_1 = (h_0*self.number) % d
        h_2 = ((inverse(2, d) * h_0 * (self.number - h_1 ** 2)) // d) % d
        b = (h_1 + h_2 * d) % a
        if b & 1 == 0:
            b -= a

        self.d_list.append(d)
        self.a_list.append(a)
        self.b_list.append(b)
        solution = []
        i = 0
        for s in self.Nsqrt:
            k = 0
            p_solution = []
            ppow = 1
            while k < len(s):
                ppow *= self.FB[i+2]
                a_inverse = inverse(2 * self.a_list[-1], ppow)
                x_1 = ((-b + s[k][0]) * a_inverse) % ppow
                x_2 = ((-b + s[k][1]) * a_inverse) % ppow
                p_solution.append([x_1, x_2])
                k += 1

            i += 1
            solution.append(p_solution)

        self.solution = solution

    def run_sieve(self):
        self.make_poly()
        M = self.Srange
        a = self.a_list[-1]
        b = self.b_list[-1]
        c = (b ** 2 - self.number) // (4 * a)
        d = self.d_list[-1]
        self.poly_table = []
        self.log_poly = []
        self.minus_check = []
        for j in self.move_range:
            jj = (a * j + b) * j + c
            if jj < 0:
                jj = -jj
                self.minus_check.append(j + M)

            elif jj == 0:
                jj = 1

            lj = int((log(jj) * 30) * 0.95)
            self.poly_table.append(jj)
            self.log_poly.append(lj)

        y = inverse(2 * d, self.number)
        start_location = []
        logp = [0] * (2 * M + 1)
        j = 2
        for i in self.solution:
            start_p = []
            ppow = 1
            for k in range(len(i)):
                ppow *= self.FB[j]
                q = -M // ppow
                s_1 = (q + 1) * ppow + i[k][0]
                s_2 = (q + 1) * ppow + i[k][1]
                while s_1 + M >= ppow:
                    s_1 -=ppow

                while s_2 + M >= ppow:
                    s_2 -= ppow

                start_p.append([s_1 + M, s_2 + M])

            start_location.append(start_p)
            j += 1

        self.start_location = start_location
        i = self.poly_table[0] & 1
        while i <= 2 * M:
            j = 1
            while self.poly_table[i] % (2 ** (j + 1)) == 0:
                j += 1

            logp[i] += self.FB_log[1] * j
            i += 2

        L = 2
        for plocation in self.start_location:
            for k in range(len(plocation)):
                s_1 = plocation[k][0]
                s_2 = plocation[k][1]
                ppow = self.FB[L] ** (k + 1)
                while s_1 <= 2 * M:
                    logp[s_1] += self.FB_log[L]
                    s_1 += ppow

                while s_2 <= 2 * M:
                    logp[s_2] += self.FB_log[L]
                    s_2 += ppow

            L += 1

        self.logp = logp
        smooth = []
        for t in range(2 * M + 1):
            if logp[t] >= self.log_poly[t]:
                poly_val = self.poly_table[t]
                index_vector = []
                H = (y * (2 * a * (t-self.Srange) + b)) % self.number
                for p in self.FB:
                    if p == -1:
                        if t in self.minus_check:
                            index_vector.append(1)

                        else:
                            index_vector.append(0)

                    else:
                        r = 0
                        while poly_val % (p ** (r + 1)) == 0:
                            r += 1

                        v = r & 1
                        index_vector.append(v)

                smooth.append([index_vector, (poly_val, H)])

        return smooth

    def get_vector(self):
        P = len(self.FB)
        if P < 100:
            V = -5

        else:
            V = 0

        smooth = []
        i = 0
        while P * 1 > V:
            n = self.run_sieve()
            V += len(n)
            smooth += n
            i += 1

        if P < 100:
            V += 5

        self.smooth = smooth
        return smooth

class Elimination():
    def __init__(self, smooth):
        self.vector = []
        self.history = []
        i = 0
        for vec in smooth:
            self.vector.append(vec[0])
            self.history.append({i:1})
            i += 1
        self.FB_number = len(self.vector[0])
        self.row_size = len(self.vector)
        self.historytime = 0

    def vector_add(self, i, j):
        V_i = self.vector[i]
        V_j = self.vector[j]
        k = 0
        while k < len(V_i):
            if V_i[k] == 1:
                if V_j[k] == 1:
                    V_j[k] = 0
                else:
                    V_j[k] = 1
            k += 1

    def transpose(self):
        Transe_vector = []
        i = 0
        while i < self.FB_number:
            j = 0
            vector = []
            while j < self.row_size:
                vector.append(self.vector[j][i])
                j += 1

            Transe_vector.append(vector)
            i += 1

        self.Transe = Transe_vector

    def history_add(self, i, j):
        H_i = self.history[i].keys()
        H_j = self.history[j].keys()
        for k in H_i:
            if k in H_j:
                del self.history[j][k]

            else:
                self.history[j][k] = 1

    def gaussian(self):
        pivot = []
        FBnum = self.FB_number
        Smooth = len(self.vector)
        for j in range(self.FB_number):
            for k in range(Smooth):
                if k in pivot or not self.vector[k][j]:
                    continue

                pivot.append(k)
                V_k = self.vector[k]
                for h in range(Smooth):
                    if h in pivot or not self.vector[h][j]:
                        continue

                    self.history_add(k, h)
                    V_h = self.vector[h]
                    for q in range(j, FBnum):
                        if V_k[q]:
                            V_h[q] = not V_h[q]
                            
                break

        self.pivot = pivot
        zero_vector = []
        for check in range(Smooth):
            if check not in pivot:
                g = 0
                while g < FBnum:
                    if self.vector[check][g] == 1:
                        break

                    g += 1

                if g == FBnum:
                    zero_vector.append(check)

        return zero_vector

def qs(n, s, f):
    Q = QS(n, s, f)
    Q.run_sieve()
    V = Elimination(Q.smooth)
    A = V.gaussian()
    answerX_Y = []
    N_factors = []
    for i in A:
        B = V.history[i].keys()
        X = 1
        Y = 1
        for j in B:
            X *= Q.smooth[j][1][0]
            Y *= Q.smooth[j][1][1]
            Y = Y % Q.number

        X = sqrt_modn(X, Q.number)
        answerX_Y.append(X - Y)

    for k in answerX_Y:
        if k != 0:
            factor = gcd(k, Q.number)
            if factor not in N_factors and factor != 1 and factor != Q.number and is_prime(factor) == 1:
                N_factors.append(factor)

    N_factors.sort()

def mpqs(n, s = 0, f = 0, m = 0):
    M = MPQS(n, s, f, m)
    M.get_vector()
    N = M.number // M.multiplier
    V = Elimination(M.smooth)
    A = V.gaussian()
    answerX_Y = []
    N_prime_factors = []
    N_factors = []
    output = []
    for i in A:
        B = V.history[i].keys()
        X = 1
        Y = 1
        for j in B:
            X *= M.smooth[j][1][0]
            Y *= M.smooth[j][1][1]
            Y %= M.number

        X = sqrt_modn(X, M.number)
        if X != Y:
            answerX_Y.append(X-Y)

    NN = 1
    for k in answerX_Y:
        factor = gcd(k, N)
        if factor not in N_factors and factor != 1 and factor != N and factor not in N_prime_factors:
            if is_prime(factor):
                NN *= factor
                N_prime_factors.append(factor)

            else:
                N_factors.append(factor)

    if NN == N:
        N_prime_factors.sort()
        for p in N_prime_factors:
            N = N // p
            i = vp(N, p, 1)[0]
            output.append((p, i))

        return output

    elif NN != 1:
        f = N // NN
        if is_prime(f):
            N_prime_factors.append(f)
            N_prime_factors.sort()
            for p in N_prime_factors:
                N = N // p
                i = vp(N, p, 1)[0]
                output.append((p, i))

            return output

    for F in N_factors:
        for FF in N_factors:
            if F != FF:
                Q = gcd(F, FF)
                if is_prime(Q) and Q not in N_prime_factors:
                    N_prime_factors.append(Q)
                    NN *= Q

    N_prime_factors.sort()
    for P in N_prime_factors:
        i, N = vp(N, P)
        output.append((P, i))

    if  N == 1:
        return output

    for F in N_factors:
        g = gcd(N, F)
        if is_prime(g):
            N_prime_factors.append(g)
            N = N // g
            i = vp(N, g, 1)[0]
            output.append((g, i))

    if N == 1:
        return output

    elif is_prime(N):
        output.append((N, 1))
        return output

    else:
        N_factors.sort()
        return output, N_factors

def eratosthenes(n):
    sieve = [True] * (n + 1)

    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i ** 2, n + 1, i):
                sieve[j] = False

    return [x for x in range(2, n + 1) if sieve[x]]

def prime_mod8(n):
    primes = eratosthenes(n)
    PrimeList = {1:[], 3:[], 5:[], 7:[]}
    LegendreList = {1:[], 3:[], 5:[], 7:[]}
    sp = [2, 3, 5, 7, 11, 13]
    for p in primes:
        if p not in sp:
            leg = [legendre(p, q) for q in sp[1:]]
            if leg not in PrimeList[p & 7]:
                LegendreList[p & 7].append(leg)
                PrimeList[p & 7].append([p, leg])

    return [PrimeList[1], PrimeList[3], PrimeList[5], PrimeList[7]]

def eratosthenes_log(n):
    primes = eratosthenes(n)
    primes_log = []
    for i in primes:
        l = int(log(i) * 30)
        primes_log.append(l)

    return primes_log

def sqrt_modn(n, modulo):
    factorOfN = _factor(n)[0]
    prod = 1
    for p, e in factorOfN:
        prod = (prod * pow(p, e >> 1, modulo)) % modulo

    return prod

def sqroot_power(a, p, n):
    x = modsqrt(a, p)
    answer = [[x, p - x]]
    ppower = p
    i = inverse(x << 1, p)
    for i in range(n - 1):
        x += (a - x ** 2) // ppower * i % p * ppower
        ppower *= p
        answer.append([x, ppower - x])

    return answer

primes_table = eratosthenes(10 ** 5)
primes_log_table = eratosthenes_log(10 ** 5)
prime_8 = prime_mod8(8090)
mpqs_p_100 = [[100, x] for x in [20, 21, 22, 24, 26, 29, 32]]
mpqs_p_300 = [[300, x] for x in [40, 60, 80, 100, 120, 140]]
mpqs_p_2000 = [[2000, x] for x in [240, 260, 280, 325, 355, 375, 400, 425, 550]]
mpqs_p_15000 = [[15000, x] for x in [1300, 1600, 1900, 2200]]
parameters_for_mpqs = mpqs_p_100 + [[200, 35]] + mpqs_p_300 + [[600, 160]] + [[900, 180]] + [[1200, 200]] + [[1000,220]] + mpqs_p_2000 + [[3000, 650]] + [[5000, 750]] + [[4000, 850]] + [[4000, 950]] + [[5000, 1000]] + [[14000, 1150]] + mpqs_p_15000 + [[20000,2500]]

def mpqsfind(n, s = 0, f = 0, m = 0):
    M = MPQS(n, s, f, m)
    M.get_vector()
    N = M.number // M.multiplier
    V = Elimination(M.smooth)
    A = V.gaussian()
    differences = []
    for i in A:
        B = V.history[i].keys()
        X = 1
        Y = 1
        for j in B:
            X *= M.smooth[j][1][0]
            Y *= M.smooth[j][1][1]
            Y %= M.number

        X = floorsqrt(X) % M.number
        if X != Y:
            differences.append(X-Y)

    for diff in differences:
        divisor = gcd(diff, N)
        if 1 < divisor < N:
            return divisor

def mpqs(n):
    num = n
    ans = []
    if is_prime(n):
        ans.append(n)
        return ans

    while True:
        r = num
        try:
            if len(str(r)) > 25:
                d = mpqsfind(num)
                ans.append(d)
                r = num // d
                if is_prime(r):
                    ans.append(r)
                    break
            
                else:
                    num = r
            
            else:
                ans = [x for x in _factor(num)[1]]
                break
        
        except TypeError:
            ans = [x for x in _factor(num)[1]]
            break
    
    ans.sort()
    return ans

def crack_key(public_key):
    '''
    public_key: (n, e)
    output(private_key): (n, e, d, p, q)
    '''
    n = public_key[0]
    e = public_key[1]
    factored = mpqs(n)
    p = factored[0]
    q = factored[1]
    phi_n = (p - 1) * (q - 1)
    exponent = 65537
    d = inverse(exponent, phi_n)
    private_key = (n, e, d, p, q)
    return private_key

def test(bits):
    key = newkeys(bits)
    pub_key = eval(str(key[0]).split('PublicKey')[1])
    msg = choice(printable).encode('ascii')
    encrypted = encrypt(msg, key[0])

    t1 = time()
    priv_key = crack_key(pub_key)
    hacked = decrypt(encrypted, PrivateKey(*priv_key)).decode('utf-8')
    t2 = time()

    print(f'Plain Text: {msg.decode()}')
    print(f'Cipher Text Using RSA {bits} bits (HEX): {b2a_hex(encrypted).decode()}')
    print(f'Hacked Plain Text: {hacked}')
    print(f'Time: {t2 - t1} seconds.')

if __name__ == '__main__':
    test(90)