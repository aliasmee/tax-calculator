#!/usr/bin/env python3
# coding: utf-8
from functools import wraps

preTax = 10000
threshold = 5000
insure = 3500
special = 1500


def Const(cls):
    @wraps(cls)
    def new_setattr(self, name, value):
        raise Exception('const: {} 不能被改变'.format(name))

    cls.__setattr__ = new_setattr
    return cls


# 2019-1-1日之前的税率及速记扣款
@Const
class _OldTaxRate(object):
    taxFirst = (0.03, 0)
    taxTwo = (0.1, 210)
    taxThree = (0.2, 1410)
    taxFour = (0.25, 2660)
    taxFive = (0.3, 4410)
    taxSix = (0.35, 7160)
    taxSeven = (0.45, 15160)


# 2019-1-1日之后的税率及速记扣款
@Const
class _NewTaxRate(object):
    taxFirst = (0.03, 0)
    taxTwo = (0.1, 2520)
    taxThree = (0.2, 16920)
    taxFour = (0.25, 31920)
    taxFive = (0.3, 52920)
    taxSix = (0.35, 85920)
    taxSeven = (0.45, 181920)


@Const
class _Const(object):
    oldTaxRate = _OldTaxRate()
    newTaxRate = _NewTaxRate()


CONST = _Const()


def oldTaxRate(taxAble) -> tuple:
    try:
        if 0 <= taxAble <= 3000:
            return CONST.oldTaxRate.taxFirst
        elif 3000 < taxAble <= 12000:
            return CONST.oldTaxRate.taxTwo
        elif 12000 < taxAble <= 25000:
            return CONST.oldTaxRate.taxThree
        elif 25000 < taxAble <= 35000:
            return CONST.oldTaxRate.taxFour
        elif 35000 < taxAble <= 55000:
            return CONST.oldTaxRate.taxThree
        elif 55000 < taxAble <= 80000:
            return CONST.oldTaxRate.taxSix
        elif taxAble > 80000:
            return CONST.oldTaxRate.taxSeven
        else:
            return None
    except Exception as e:
        raise "请输入正确的数字"


def newTaxRate(taxAble):
    try:
        if 0 <= taxAble <= 36000:
            return CONST.newTaxRate.taxFirst
        elif 36000 < taxAble <= 144000:
            return CONST.newTaxRate.taxTwo
        elif 144000 < taxAble <= 300000:
            return CONST.newTaxRate.taxThree
        elif 300000 < taxAble <= 420000:
            return CONST.newTaxRate.taxFour
        elif 420000 < taxAble <= 660000:
            return CONST.newTaxRate.taxFive
        elif 660000 < taxAble <= 960000:
            return CONST.newTaxRate.taxSix
        elif taxAble > 960000:
            return CONST.newTaxRate.taxSeven
        else:
            return None
    except Exception as e:
        raise "请输入正确的数字"


class CalcTax(object):
    """计算所缴纳的税"""

    # 工资、社保、专项扣除，第几期（以1年12个月计算，共12期）
    def __init__(self, salary, socialSec=0, special=0, time=1, isNewTax=True):
        self.salary = salary
        self.socialSec = socialSec
        self.special = special
        self.time = time
        self.isNewTax = isNewTax

    # 默认三险一金
    def defaultSociaSec(self):
        return self.salary * (0.08 + 0.02 + 0.12)

    def taxAble(self):
        # 计算应纳税所得额, 每月固定额度，返回一个列表
        if self.socialSec > 0:
            _taxAble = self.salary - threshold - self.socialSec
        else:
            socialSec = self.defaultSociaSec()
            _taxAble = self.salary - threshold - socialSec
        return _taxAble

    def oldCalcTax(self):
        # if self.socialSec > 0:
        #     taxAble = self.salary - threshold - self.socialSec
        # else:
        #     socialSec = self.defaultSociaSec()
        #     taxAble = self.salary - threshold - socialSec
        _taxAble = self.taxAble()
        if oldTaxRate(_taxAble) != None:
            tax = _taxAble * oldTaxRate(_taxAble)[0] - oldTaxRate(_taxAble)[1]
        return float('%.2f' % tax)

    def newCalcTax(self) -> list:
        # 2019 改革后，新税采用累加计算，所以次月交的可能会比上月的高
        i = 1
        totalTax = 0
        taxList = []
        taxRateList = []
        mounth = []
        if self.socialSec > 0:
            socialSec = self.socialSec
        elif self.socialSec == 0 or self.socialSec is None:
            socialSec = self.defaultSociaSec()

        while i <= self.time:
            taxTotalAble = (self.salary - threshold - socialSec - self.special) * i
            if newTaxRate(taxTotalAble)[0] != None:
                tax = taxTotalAble * newTaxRate(taxTotalAble)[0] - newTaxRate(taxTotalAble)[1] - totalTax
                taxRateList.append((newTaxRate(taxTotalAble)[0]))

                taxList.append(float('%.2f' % tax))
                totalTax = totalTax + (
                        taxTotalAble * newTaxRate(taxTotalAble)[0] - newTaxRate(taxTotalAble)[1] - totalTax)
            mounth.append(i)
            i += 1
        tax = zip(taxRateList, taxList)
        tax2 = dict(zip(mounth, tax))
        return tax2

    # 打印每个月的应缴，以及适用税率
    def printYear(self, taxRateDict):
        _getRateList = taxRateDict
        if not self.isNewTax:
            for i in range(1,13):
                print("第{0}个月应缴税：{1}, 适用 {2}% 税率.".format(i, _getRateList, oldTaxRate(self.taxAble())[0]))
        else:
            for i in _getRateList:
                print("第{0}个月应缴税：{1}, 适用 {2}% 税率.".format(i, _getRateList[i][1], _getRateList[i][0]))


# 打印出一年总共要较耐的税
def oldTotalTax(salary, socialSec=0):
    oldTax = CalcTax(salary, socialSec)
    return oldTax.oldCalcTax() * 12


def newTotalTax(salary, socialSec=0, special=0, time=1):
    newTax = CalcTax(salary, socialSec, special, time).newCalcTax()
    totalTax = 0
    for tax in newTax:
        totalTax += newTax[tax][1]
    return totalTax


def main():
    _salary = int(input("请输入你的税前工资： "))
    _socialSec = float(input("请输入你的三险一金（如不填的话，将按照工资正常扣除）： ") or "0")
    _special = int(input("请输入你的专项扣税总额（如租房、贷款、学历教育、子女教育、老人等,Default：0)：") or "0")
    _phase = int(input("请输入你要计算的周期(Tips: 新税采用累加政策，每月税款可能不一样): ") or "1")
    _choice = int(input("是否计算每年能省下来都少钱？(0 or 1, Default: 0): ") or "0")
    try:
        if _socialSec > _salary or _special > _salary:
            print("三险一金、专项扣除金额不能大于你的工资！请重新运行程序！")
        elif _salary > 0 and _socialSec >= 0 and _special >= 0:
            _newTax = CalcTax(_salary, _socialSec, _special, _phase).newCalcTax()
            CalcTax(_salary, _socialSec, _special, _phase).printYear(_newTax)

    except TypeError:
        print("Error Messages: 三险一金、专项扣除金额不能大于你的工资！请重新运行程序！")
        raise
    if _choice == 0:
        print("今年一共需缴纳税额{0:.1f}人民币，相比税改之前可以节省{1:.1f}人民币！".format(newTotalTax(_salary,_socialSec,_special,12),oldTotalTax(_salary,_socialSec)-newTotalTax(_salary,_socialSec,_special,12)))

        # oldTax = CalcTax(salary=_salary, socialSec=_socialSec, isNewTax=False).oldCalcTax()
        # CalcTax(salary=_salary, socialSec=_socialSec, isNewTax=False).printYear(oldTax)



if __name__ == '__main__':
    main()