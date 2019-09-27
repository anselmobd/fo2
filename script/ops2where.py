with open('/home/anselmo/ops_dboracle.txt') as ops:
    i = 0
    for op in ops:
        print(op.strip(), end=', ')
        i += 1
        if i == 20:
            i = 0
            print('')
