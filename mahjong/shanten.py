from kago_utils.hai import Hai34, Hai34List
from kago_utils.shanten import Shanten


# 牌番号がny以上の有効牌を返す関数
def get_yuko(jun: Hai34, n_huro=0):
    yuko = []

    jun = jun.to_hai34_counter()
    current_shanten = Shanten.calculate_shanten(jun, n_huro)

    for i in range(34):
        if jun.data[i] < 4:
            next_jun = jun + Hai34List([i])
            next_shanten = Shanten.calculate_shanten(next_jun, n_huro)
            if next_shanten < current_shanten:
                yuko.append(i)

    return yuko
