from itertools import product
from pprint import pprint


def grade_minima(qtds, max_erro):
    total = sum(qtds)
    max_value = 1
    while max_value <= 9:
        grades = product(
            range(max_value+1), repeat=len(qtds))
        best = {'grade': [], 'erro': 1}
        for grade in grades:
            if max(grade) < max_value:
                continue
            tot_grade = sum(grade)
            diff = 0
            for i in range(len(qtds)):
                qtd_grade = total / tot_grade * grade[i]
                diff += abs(qtd_grade - qtds[i])
            if best['erro'] > (diff / total):
                best['erro'] = diff / total
                best['grade'] = grade
        if best['erro'] <= max_erro:
            break
        max_value += 1
    return best['grade'], best['erro']
