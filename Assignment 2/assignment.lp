Minimize
    r
Subject to
    dems1d1 : xs1t1d1 = 40
    dems1d2 : xs1t1d2 = 30
    dems2d1 : xs2t1d1 = 10
    dems2d2 : xs2t1d2 = 60
    caps1t1 : xs1t1d1 + xs1t1d2 - 100r <= 0
    caps2t1 : xs2t1d1 + xs2t1d2 - 100r <= 0
    capt1d1 : xs1t1d1 + xs2t1d1 - 100r <= 0
    capt1d2 : xs1t1d2 + xs2t1d2 - 100r <= 0
Bounds
    xs1t1d1 >= 0
    xs2t1d1 >= 0
    xs1t1d2 >= 0
    xs2t1d2 >= 0
End