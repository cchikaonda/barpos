from django import conf
from pos.models import *
from constance import config

def get_mpamba_bill(balance):
    bill = balance
    service_fee = get_service_fee(bill)
    mpamba_service_fee = Money(service_fee, 'MWK')
    mpamba_bill = Money(0.0, 'MWK')
    mpamba_bill = mpamba_service_fee + bill
    return mpamba_bill
    
def get_service_fee(balance):
    bill = balance
    if bill >= Money(50.00, 'MWK') and bill <= Money(500.00, 'MWK'):
        return float(config.BTN_50_500)
    elif bill >= Money(501.00, 'MWK') and bill <= Money(900.00, 'MWK'):
        return float(config.BTN_501_900)
    elif bill >= Money(901.00, 'MWK') and bill <= Money(1000.00, 'MWK'):
        return float(config.BTN_901_1000)
    elif bill >= Money(1001.00,'MWK') and bill <= Money(2400.00, 'MWK'):
        return float(config.BTN_1001_2400)
    elif bill >= Money(2401.00, 'MWK') and bill <= Money(2500.00, 'MWK'):
        return float(config.BTN_2401_2500)
    elif bill >= Money(2501.00, 'MWK') and bill <= Money(4900.00, 'MWK'):
        return float(config.BTN_2501_4900)
    elif bill >= Money(4901.00, 'MWK') and bill <= Money(5000.00, 'MWK'):
        return float(config.BTN_4901_5000)
    elif bill >= Money(5001.00, 'MWK') and bill <= Money(9900.00, 'MWK'):
        return float(config.BTN_5001_9900)
    elif bill >= Money(9901.00, 'MWK') and bill <= Money(10000.00, 'MWK'):
        return float(config.BTN_9901_10000)
    elif bill >= Money(10001.00, 'MWK') and bill <= Money(14900.00, 'MWK'):
        return float(config.BTN_10001_14900)
    elif bill >= Money(15001.00, 'MWK') and bill <= Money(15900.00, 'MWK'):
        return float(config.BTN_15001_15900)
    elif bill >= Money(15901.00, 'MWK') and bill <= Money(20000.00, 'MWK'):
        return float(config.BTN_15901_20000)
    elif bill >= Money(20001.00, 'MWK') and bill <= Money(25000.00, 'MWK'):
        return float(config.BTN_20001_25000)
    
    elif bill >= Money(25001.00, 'MWK') and bill <= Money(30000.00, 'MWK'):
        return float(config.BTN_25001_30000)
    elif bill >= Money(30001.00, 'MWK') and bill <= Money(40000.00, 'MWK'):
        return float(config.BTN_30001_40000)
    elif bill >= Money(40001.00, 'MWK') and bill <= Money(50000.00, 'MWK'):
        return float(config.BTN_40001_50000)
    elif bill >= Money(50001.00, 'MWK') and bill <= Money(60000.00, 'MWK'):
        return float(config.BTN_50001_60000)

    elif bill >= Money(60001.00, 'MWK') and bill <= Money(80000.00, 'MWK'):
        return float(config.BTN_60001_80000)
    elif bill >= Money(80001.00, 'MWK') and bill <= Money(100000.00, 'MWK'):
        return float(config.BTN_80001_100000)
    elif bill >= Money(100001.00, 'MWK') and bill <= Money(125000.00, 'MWK'):
        return float(config.BTN_100001_125000)
    elif bill >= Money(125001.00, 'MWK') and bill <= Money(150000.00, 'MWK'):
        return (config.BTN_125001_150000)
    
    elif bill >= Money(150001.00, 'MWK') and bill <= Money(200000.00, 'MWK'):
        return float(config.BTN_150001_200000)
    elif bill >= Money(200001.00, 'MWK') and bill <= Money(300000.00, 'MWK'):
        return float(config.BTN_200001_300000)
    elif bill >= Money(300001.00, 'MWK') and bill <= Money(400000.00, 'MWK'):
        return float(config.BTN_300001_400000)
    elif bill >= Money(400001.00, 'MWK') and bill <= Money(500000.00, 'MWK'):
        return float(config.BTN_400001_500000)
    
    elif bill >= Money(500001.00, 'MWK') and bill <= Money(600000.00, 'MWK'):
        return float(config.BTN_500001_600000)
    elif bill >= Money(600001.00, 'MWK'):
        return float(config.BTN_600001_750000)
    else:
        return bill.amount
    
