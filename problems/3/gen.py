import random

for id in range(30):
    a = random.randint(1, 100)
    b = random.randint(1, 100)

    # write into "./in/{id}.txt"
    with open("./in/{}.txt".format(id), "w") as f:
        f.write("{} {}\n".format(a, b))

    ans = a + b

    # write into "./out/{id}.txt"
    with open("./out/{}.txt".format(id), "w") as f:
        f.write("{}\n".format(ans))

# for id in range(30):
#     print("{")
#     print("\"input\": \"in/{}.txt\",".format(id))
#     print("\"output\": \"out/{}.txt\"".format(id))
#     print("},")
