import random

for id in range(20):
    n = random.randint(1, 10**3)

    # write into "./in/{id}.txt"
    with open("./in/{}.txt".format(id), "w") as f:
        f.write("{}\n".format(n))

    ans = 0
    for i in range(n):
        ans += (i + 1)**2

    # write into "./out/{id}.txt"
    with open("./out/{}.txt".format(id), "w") as f:
        f.write("{}\n".format(ans))

# for id in range(40):
#     print("{")
#     print("\"input\": \"in/{}.txt\",".format(id))
#     print("\"output\": \"out/{}.txt\"".format(id))
#     print("},")
