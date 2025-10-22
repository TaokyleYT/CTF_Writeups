import hashlib

def knuth(seed):
    result = seed
    for i in range(1, 10**9):
        result = (result * i + 3) % 2**32
        result = (result ^ (result >> 3)) & 0xFFFFFFFF
        result = (result * 2654435761) % 2**32

    return result

def flag():
    result = knuth(95714287)
    hex_string = hashlib.sha256(str(result).encode()).hexdigest()[:32]
    return hex_string

if __name__ == '__main__':
    print(str(flag())+'}')