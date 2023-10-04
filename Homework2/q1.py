# 1. (40 points) The security of RSA public key cryptosystem relies on the fact that prime factorization of large integers is practically unsolvable due to the high time-complexity of its solution. Here is the reason:

# Part of RSA's public key is a semiprime number  that is the product of two very large prime numbers  and . Although  is publicly available, both and  must remain secret; otherwise, RSA's private key can be easily calculated and RSA's security gets compromised.

# a) Complete the implementation of the following Python function that finds the prime factors  and  of a given semiprime number  so that :

# def semiprime_factorize(n):
#     #precondition: n is a semiprime number: n = p.q
#     #returns the ordered pair of prime numbers (p,q)
#     #your code here...
# Hint: to do this factorization, try dividing  by one of the following  values: . Since  has only two prime factors, it must be divisible by one of these values.

# b) The python code available here implements an experiment to find the time-complexity of your solution in part (a) for the prime factorization problem. This experiment uses your solution to factorize random semiprime integers  with different lengths from 32-bits to 64-bits. The given Python code prints out the average time it takes for your solution to factorize random semiprime integers.

# c) Plot the values printed by the experiment in part (b). Using linear extrapolation, estimate the time it takes for your computer to break RSA with 2048-bit key. Please note that the results printed in part b are the logarithms of actual time in seconds.




# -*- coding: utf-8 -*-
"""
Created on Fri Sep 30 19:53:36 2022

@author: drbor
"""

import math
import random
import time
def random_prime(n):
    #generates a random n-bit prime number
    if n < 2:
        return -1
    max = 1 << n
    while True:
        r = random.randrange(2, max+1)
        if primality_test(r, 40):
            return r
    
def primality_test(n, iterations):
    if ~n & 1 or n == 3:
        if n == 2 or n == 3:
            return True
        else:
            return False
    q = n - 1
    k = 0
    while ~q & 1:
        q >>= 1
        k += 1
    for iteration in range(iterations):
        a = random.randrange(2,n-1)
        rem = pow(a, q, n)
        if rem == n-1 or rem == 1:
            continue
        inconclusive = False
        for j in range(1, k):
            rem = pow(rem, 2, n)
            if rem == n - 1:
                inconclusive = True
                break
        if not inconclusive:#composite
            return False
    return True
def semiprime_factorize(n):
    #precondition: n is a semiprime number: n = p.q
    #returns the ordered pair of prime numbers (p,q)
    #your code is here...
    for p in range(2,int(math.sqrt(n))+1):
        if n%p == 0:
            q = n//p
            if is_prime(p) and is_prime(q):
                return (p,q)
def is_prime(num):
    if num < 2:
        return False
    for i in range(2,int(math.sqrt(num))+1):
        if num%i == 0:
            return False
    return True

  
print('key length','\t', 'log(time)')

key_lengths = []
log_times = []

for nbits in range(32, 65, 2):
    avg_time = 0
    for _ in range(20):
        p = random_prime(nbits >> 1)
        q = random_prime(nbits >> 1)
        t0 = time.time()
        (calculated_p, calculated_q) = semiprime_factorize(p * q)
        elapsed = time.time() - t0
        if (p, q) != (calculated_p, calculated_q) and (p, q) != (calculated_q, calculated_p):
            print("Error: incorrect prime factorization", (p, q), (calculated_p, calculated_q))
        avg_time += elapsed / 20
    if avg_time != 0:
        print(nbits, '\t\t\t', round(math.log10(avg_time) * 100) / 100)
        key_lengths.append(nbits)
        log_times.append(round(math.log10(avg_time) * 100) / 100)