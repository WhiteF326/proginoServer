import random

for id in range(40):
    a = random.randint(1, 1000)
    b = random.randint(1, 1000)
    c = ["+", "-", "*"][random.randint(0, 2)]

    # write into "./in/{id}.txt"
    with open("./in/{}.txt".format(id), "w") as f:
        f.write("{} {}\n".format(a, b))
        f.write("{}\n".format(c))

    if c == "+":
        ans = a + b
    elif c == "-":
        ans = a - b
    else:
        ans = a * b

    # write into "./out/{id}.txt"
    with open("./out/{}.txt".format(id), "w") as f:
        f.write("{}\n".format(ans))

# for id in range(40):
#     print("{")
#     print("\"input\": \"in/{}.txt\",".format(id))
#     print("\"output\": \"out/{}.txt\"".format(id))
#     print("},")
