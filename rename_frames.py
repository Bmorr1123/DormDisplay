import os


files = os.listdir("frames")

longest = 0
for file in files:
    number = file[file.find("_") + 1:file.find(".")]
    longest = max(longest, len(number))

for file in files:
    number = file[file.find("_") + 1:file.find(".")]
    while len(number) < longest:
        number = f"0{number}"
    os.rename(f"frames/{file}", f"frames/frame_{number}.png")