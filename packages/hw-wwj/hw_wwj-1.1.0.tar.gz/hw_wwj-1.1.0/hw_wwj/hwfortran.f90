real*8 function hw1(r1, r2)
real*8 :: r1, r2
!f2py intent(in) r1
!f2py intent(in) r2
hw1 = sin(r1 + r2)
print*, hw1
return
end function hw1

subroutine hw2(r1, r2)
real*8 :: r1, r2, s
!f2py intent(in) r1
!f2py intent(in) r2
s = sin(r1 + r2)
print*, 'Hello, World!, sin(',r1+r2,')=',s
return
end subroutine hw2

subroutine hw3(r3, r4, s)
! integer, intent(in) :: r3, r4 这里不能用integer（整型），否则会报错
real, intent(in) :: r3,r4
real, intent(out) :: s
!f2py intent(in) r3
!f2py intent(in) r4
!f2py intent(out) s
s = sin(r3 + r4)
return
end
