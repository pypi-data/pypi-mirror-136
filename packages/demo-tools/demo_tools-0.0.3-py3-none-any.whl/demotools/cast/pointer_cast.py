def int_char_int(val1, val2, val3):
    s1 = bin(val1)[2:]
    s1 = (32 - len(s1)) * '0' + s1
    s1 = s1[::-1]
    s2 = bin(val2)[2:]
    s2 = (32 - len(s2)) * '0' + s2
    s2 = s2[::-1]
    s3 = bin(val3)[2:]
    s3 = (32 - len(s3)) * '0' + s3
    s3 = s3[::-1]
    s4 = s1[:8] + s3 + s2[8:]
    s5 = s4[:32]
    s6 = s4[32:]
    r1 = int(s5[::-1], base=2)
    r2 = int(s6[::-1], base=2)
    print(val1, val2, val3, r1, r2)
