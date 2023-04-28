
# params

defaults = 10_000

loans = 80_000 - defaults
zSTT = 70_000
zJTT = 30_000

if defaults >= zJTT:
    zSTT = zSTT - (defaults - zJTT)
    zJTT = 0
else:
    zJTT = zJTT - defaults

apyLoans = 0.18
apySTT = 0.08
apyJTT = 0.15

yieldGen = loans * apyLoans
print('yieldGen: ', yieldGen)
print('~')

print('PRE REDEEM')
yieldSTT = zSTT * apySTT
yieldJTT = zJTT * apyJTT
print('yieldZVE: ', yieldGen * 0.2)
print('yieldSTT: ', yieldSTT)
print('yieldJTT: ', yieldJTT)
print('residual: ', yieldGen - yieldGen * 0.2 - yieldSTT - yieldJTT)
print('~')

# print('REDEEM zJTT')
# redeemAmount = 10_000
# print('redeemAmount: ', redeemAmount)
# assert(redeemAmount <= 10_000)
# zJTT = zJTT - redeemAmount
# yieldGen = loans * apyLoans
# print('yieldGen: ', yieldGen)
# print('~')

# print('REDEEM zSTT')
# redeemAmount = 10_000
# print('redeemAmount: ', redeemAmount)
# assert(redeemAmount <= 10_000)
# zSTT = zSTT - redeemAmount
# yieldGen = loans * apyLoans
# print('yieldGen: ', yieldGen)
# print('~')

# print('REDEEM zJTT, WIPE DEBT')
# redeemAmount = 10_000
# print('redeemAmount: ', redeemAmount)
# assert(redeemAmount <= 10_000)
# # zJTT = zJTT - redeemAmount
# yieldGen = loans * apyLoans
# print('yieldGen: ', yieldGen)
# print('~')

print('REDEEM zSTT, WIPE DEBT')
redeemAmount = 15_000
print('redeemAmount: ', redeemAmount)
assert(redeemAmount <= 15_000)
zSTT = zSTT - redeemAmount
zJTT = zJTT + redeemAmount
yieldGen = loans * apyLoans
print('yieldGen: ', yieldGen)
print('~')

print('POST REDEEM')
yieldSTT = zSTT * apySTT
yieldJTT = zJTT * apyJTT
print('yieldZVE: ', yieldGen * 0.2)
print('yieldSTT: ', yieldSTT)
print('yieldJTT: ', yieldJTT)
print('residual: ', yieldGen - yieldGen * 0.2 - yieldSTT - yieldJTT)
print('~')