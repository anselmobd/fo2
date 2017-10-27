

def group_rowspan(data, group):
    noSpan = True
    for i in range(len(data)):
        data[i]['rowspan'] = 1
    inferior = []
    atual = []
    for i in range(len(data)-1, -1, -1):
        atual = [data[i][f] for f in group]
        if atual == inferior:
            noSpan = False
            data[i]['rowspan'] = data[i]['rowspan'] + data[i+1]['rowspan']
            data[i+1]['rowspan'] = 0
        inferior = atual[:]
    if noSpan:
        del group[:]
