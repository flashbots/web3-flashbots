
# rAJ = redemptionsAllowedJunior
# rAS = redemptionsAllowedSenior
# eDJ = epochDiscountJunior
# eDS = epochDiscountSenior
# sP  = stablecoinsPresent

def burn(rAJ, rAS, eDJ, eDS, sP):
    assert(eDJ <= 10000)
    assert(eDS <= 10000)
    totalAllowed = rAJ * (10000 - eDJ) // 10000 + rAS * (10000 - eDS) // 10000
    print('totalAllowed', totalAllowed)
    portion = sP / totalAllowed
    if portion > 1:
        portion = 1
    print('portion', portion)
    print('returnedStablecoins burn seniorPortion', portion * rAS * (10000 - eDS) / 10000)
    print('returnedStablecoins burn juniorPortion', portion * rAJ * (10000 - eDJ) / 10000)
    print('returnedStablecoins total', portion * rAS * (10000 - eDS) / 10000 + portion * rAJ * (10000 - eDJ) / 10000)


burn(200_000, 1_000_000, 5000, 0, 100_000)
