a, b = map(int, input().split())
c = input()

if c == "+":
    ans = a + b
elif c == "-":
    ans = a - b
else:
    ans = a * b
print(ans)
