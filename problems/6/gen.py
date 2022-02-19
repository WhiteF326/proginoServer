import random

for id in range(40):
    n = random.randint(1, 10**9)

    # write into "./in/{id}.txt"
    with open("./in/{}.txt".format(id), "w") as f:
        f.write(str(n) + "\n")

    ans = ""
    while n:
        ans = str(n % 2) + ans
        n >>= 1

    # write into "./out/{id}.txt"
    with open("./out/{}.txt".format(id), "w") as f:
        f.write("{}\n".format(ans))

# for id in range(40):
#     print("{")
#     print("\"input\": \"in/{}.txt\",".format(id))
#     print("\"output\": \"out/{}.txt\"".format(id))
#     print("},")
