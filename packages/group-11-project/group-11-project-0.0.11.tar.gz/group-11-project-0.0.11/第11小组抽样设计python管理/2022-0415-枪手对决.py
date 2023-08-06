#枪手对决
function A=Leo(A,p1,p2,p3)
if A(1,1)==1&rand<p1
    if A(2,1)==1
        A(2,1)=0;
    elseif A(3,1)==1
        A(3,1)=0;
    else
    end
end
end


function A=Raph(A,p1,p2,p3)
if A(2,1)==1&rand<p2
    if A(1,1)==1
        A(1,1)=0;
    elseif A(3,1)==1
        A(3,1)=0;
    else
    end
end
end

#最弱的Mikey ，反而有很强的能动性 Mikey不放空枪的情况：

function A=Mikey(A,p1,p2,p3)
if A(3,1)==1&rand<p3
    if A(1,1)==1&A(2,1)==0
        A(1,1)=0;
    elseif A(1,1)==0&A(2,1)==1
        A(2,1)=0;
    elseif A(1,1)==1&A(2,1)==1
        A(1,1)=0;
    end
end
end

#如果Leo和Raph都没死，那么Mikey故意放空枪：

function A=Mikey(A,p1,p2,p3)
if A(3,1)==1&rand<p3
    if A(1,1)==1&A(2,1)==0
        A(1,1)=0;
    elseif A(1,1)==0&A(2,1)==1
        A(2,1)=0;
    elseif A(1,1)==1&A(2,1)==1
        A=A;
    end
end
end

#构建决斗场：

while sum(A)>=2%
    A=Leo(A,p1,p2,p3);
    A=Raph(A,p1,p2,p3);
    A=Mikey(A,p1,p2,p3);
end

#下面的程序把这场决斗重复一万次，并对结果进行计数

function C=main3()

B=[0;0;0];
for i=1:10000
    B=B+dual();
end
C=B./sum(B);
end

