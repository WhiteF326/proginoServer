n = int(input())
ans = ""
while n:
    ans = str(n % 2) + ans
    n >>= 1
print(ans)
