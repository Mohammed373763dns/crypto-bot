name = [
    ['6a cables'],
    ['sunglass','Wireless Mouse','Mouse','Rechargable Moouse','Trans Mouse'],
    ['adapter','TC Earphones']
    ]

Yuan_Price = [
    [0.726666],
    [24.3 , 8.8 , 4.2 , 22.5 , 14.3],
    [10.9 , 6.3]
    ]

product_quantity = [
    [3000],
    [50 , 50 , 50 , 50 , 50],
    [100 , 100]
    ]

i_delivery = [93,130,0]

cbm = [0.29,0.15,0.06]
transfer_price = 17000
total_shipping_cost = 31


i_delivery_per_piece = []
for quantities, delivery in zip(product_quantity, i_delivery):
    total_qty = sum(quantities)
    i_delivery_per_piece.append(delivery / total_qty)


#جمع الكميات
total_quantity = 0
for product_quantity_sublist in product_quantity:
    for number in product_quantity_sublist:  
        total_quantity += number


total_cbm = sum(cbm)
cmb_100 = []
#تكلفة كل بند حسب cbm
cost_per_cbm = []


for products_cbm in cbm:
    cmb_100.append(round((products_cbm/total_cbm)*100,9))

for cmb_100_pp in cmb_100:
    cost_per_cbm.append(round((cmb_100_pp/100)*total_shipping_cost,9))
#print(cost_per_cbm,'OMR')

shipping_price_per_piece = []
for quantities, cost_percbm in zip(product_quantity, cost_per_cbm):
    total_qty = sum(quantities)
    shipping_price_per_piece.append(round(cost_percbm / total_qty,9))
#print(shipping_price_per_piece)

#################################################
OMR_price = []

for Yuan_Price_sublist, in_dilivery,shipping_price_p_p in zip(Yuan_Price,i_delivery_per_piece,shipping_price_per_piece):
    new_sublist = []
    for product_price in Yuan_Price_sublist:
        new_sublist.append(round((((product_price+in_dilivery) * 1000) / transfer_price)+shipping_price_p_p,3))
    OMR_price.append(new_sublist)

#print(OMR_price)
for p_name,OMRprice in zip(name,OMR_price):
    for p_name,OMprice in zip(p_name,OMRprice):
        print(p_name,'/', OMprice)