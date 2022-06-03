from django import conf
from pos.models import *
from constance import config

def get_airtel_bill(balance):
    bill = balance
    service_fee = get_service_fee(bill)
    airtel_service_fee = Money(service_fee, 'MWK')
    airtel_bill = Money(0.0, 'MWK')
    airtel_bill = airtel_service_fee + bill
    return airtel_bill

def get_service_fee(balance):
    bill = balance
    if bill >= Money(50.00, 'MWK') and bill <= Money(499.00, 'MWK'):
        return float(config.ABTN_50_499)
    elif bill >= Money(500.00, 'MWK') and bill <= Money(999.00, 'MWK'):
        return float(config.ABTN_500_999)
    elif bill >= Money(1000.00, 'MWK') and bill <= Money(2499.00, 'MWK'):
        return float(config.ABTN_1000_2499)
    elif bill >= Money(2500.00,'MWK') and bill <= Money(4999.00, 'MWK'):
        return float(config.ABTN_2500_4999)
    elif bill >= Money(5000.00, 'MWK') and bill <= Money(9999.00, 'MWK'):
        return float(config.ABTN_5000_9999)
    elif bill >= Money(10000.00, 'MWK') and bill <= Money(14999.00, 'MWK'):
        return float(config.ABTN_10000_14999)
    elif bill >= Money(15000.00, 'MWK') and bill <= Money(19999.00, 'MWK'):
        return float(config.ABTN_15000_19999)
    elif bill >= Money(20000.00, 'MWK') and bill <= Money(24999.00, 'MWK'):
        return float(config.ABTN_20000_24999)
    elif bill >= Money(25000.00, 'MWK') and bill <= Money(29999.00, 'MWK'):
        return float(config.ABTN_25000_29999)
    elif bill >= Money(30000.00, 'MWK') and bill <= Money(39999.00, 'MWK'):
        return float(config.ABTN_30000_39999)
    elif bill >= Money(40000.00, 'MWK') and bill <= Money(49999.00, 'MWK'):
        return float(config.ABTN_40000_49999)
    elif bill >= Money(50000.00, 'MWK') and bill <= Money(59999.00, 'MWK'):
        return float(config.ABTN_50000_59999)
    elif bill >= Money(60000.00, 'MWK') and bill <= Money(79999.00, 'MWK'):
        return float(config.ABTN_60000_79999)
    elif bill >= Money(80000.00, 'MWK') and bill <= Money(99999.00, 'MWK'):
        return float(config.ABTN_80000_99999)
    elif bill >= Money(10000.00, 'MWK') and bill <= Money(50000.00, 'MWK'):
        return float(config.ABTN_100000_124999)
    elif bill >= Money(125000.00, 'MWK') and bill <= Money(149000.00, 'MWK'):
        return float(config.ABTN_125000_149999)
    elif bill >= Money(150000.00, 'MWK') and bill <= Money(199999.00, 'MWK'):
        return float(config.ABTN_150000_199999)
    elif bill >= Money(200000.00, 'MWK') and bill <= Money(299999.00, 'MWK'):
        return float(config.ABTN_200000_299999) 
    elif bill >= Money(300000.00, 'MWK') and bill <= Money(399999.00, 'MWK'):
        return float(config.ABTN_300000_399999)
    elif bill >= Money(400000.00, 'MWK'):
        return float(config.ABTN_400000_ABOVE)
    else:
        return bill.amount
    
