
# params

coupon_senior = .0825
coupon_junior = .15
fairValue = 1
# price = .75
maturity = 3

for price in range(70, 115):
    ytm_senior = (coupon_senior + (fairValue - price/100) / maturity) / ((fairValue + price/100) / 2)
    print('YTM Senior @ ', price / 100, ' -> ', round(ytm_senior * 100, 3), ' % APY')

for price in range(70, 115):
    ytm_junior = (coupon_junior + (fairValue - price/100) / maturity) / ((fairValue + price/100) / 2)
    print('YTM Junior @ ', price / 100, ' -> ', round(ytm_junior * 100, 3), ' % APY')
