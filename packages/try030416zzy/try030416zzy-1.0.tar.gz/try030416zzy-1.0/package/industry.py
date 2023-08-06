#参数
ef=1.229 #电力折煤系数 1.229吨/万度
def getElectricity(el):
    result=el*ef
    print("折煤耗电量=",result,"（吨）")
    return result