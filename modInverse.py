import gcd

def findModInverse(a,m):
    # return the modular inverse of a % m, which is the number x such that a*x % m = 1

    if gcd.gcd(a,m) != 1:
        return None # No mod inverse if a & m aren't relatively prime
    
    u1, u2, u3 = 1, 0, a
    v1, v2, v3 = 0, 1, m
    while v3 != 0:
        q = u3 // v3 
        v1, v2, v3, u1, u2, u3 = (u1 - q * v1), (u2 - q * v2), (u3 - q * v3), v1, v2, v3

    return u1 % m