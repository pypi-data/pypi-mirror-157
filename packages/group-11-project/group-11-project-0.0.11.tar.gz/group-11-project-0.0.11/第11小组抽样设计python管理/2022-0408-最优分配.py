import math
def best(N,p,N1,N2,N3,S1,S2,S3,c1,c2,c3):#定义函数计算
    n1=N*0.1*N1*S1/math.sqrt(c1)/(N1*S1/math.sqrt(c1)+N2*S2/math.sqrt(c2)+N3*S3/math.sqrt(c3))
    n2=N*0.1*N2*S2/math.sqrt(c2)/(N1*S1/math.sqrt(c1)+N2*S2/math.sqrt(c2)+N3*S3/math.sqrt(c3))
    n3=N*0.1*N3*S3/math.sqrt(c3)/(N1*S1/math.sqrt(c1)+N2*S2/math.sqrt(c2)+N3*S3/math.sqrt(c3))
    return n1,n2,n3
best(908,0.1,299, 303, 306,92, 103, 81,76,88,82)