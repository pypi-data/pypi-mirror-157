def HarmonicMean(list):
    sum = 0.0
    for i in list:
        sum += 1/i

    return round((len(list)/sum),5)
