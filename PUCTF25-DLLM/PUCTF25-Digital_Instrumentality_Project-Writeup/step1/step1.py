with open("Fanta_file_new", "rb") as f:
    cont = f.read()

padded = cont.split(b"File starts right after this sentence")
not_padded = []
for n in padded:
    not_padded.append(n.split(b"File ends right before this sentence")[0])

for n in range(3):
    with open("Fanta"+str(n), "wb") as f:
        f.write(not_padded[n])