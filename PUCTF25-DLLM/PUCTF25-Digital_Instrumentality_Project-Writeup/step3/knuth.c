#include <stdio.h>
#include <stdint.h>

//original function
/*
uint32_t knuth1(uint32_t seed) {
    uint32_t result = seed;
    for (uint32_t i = 1; i < 1000000000; i++) {
        result = (result * i + 3) % 4294967296; // 2**32
        result = (result ^ (result >> 3)) & 0xFFFFFFFF;
        result = (result * 2654435761) % 4294967296; // 2**32
    }
    return result;
}
*/

uint32_t knuth(uint32_t seed) {
    uint32_t result = seed;
    uint32_t factor = 2654435761;
    for (uint32_t i = 1; i < 1000000000; i++) {
        result = (result * i + 3);
        result ^= result >> 3;
        result *= factor;
    }
    return result;
}


int main() {
    printf("%u\n", knuth(95714287));
    return 0;
}