from pytube import YouTube
import time

print('''Welcome to Zockbot YouTube Downloader and Converter v0.2 Alpha''')
print('''Loading...\n''')
time.sleep(5)

link = input("Enter the youtube link: ")
yt = YouTube(link)

time.sleep(3)
print("\n" + "Get Video pls wait...\n")
time.sleep(5)

print("Title: ",yt.title)
print("Number of views: ",yt.views)
print("Length of video: ",yt.length,"seconds")
print("Ratings: ",yt.rating, "\n")
time.sleep(3)

print("Do u want to download it? Please choose: \n")
print("(1) Yes! \n" + "(2) No! \n")

choice = input("Choice: ")

if choice == "1":
    time.sleep(3)
    print("\n" + "Please wait while getting Video Streams...\n")
    time.sleep(3)
    path = input("Download location: \n")
    time.sleep(3)
    print("Try to get Download... \n")
    ys = yt.streams.get_highest_resolution()
    time.sleep(3)
    print(f"Downloading {yt.title}... \n")
    ys.download(path)
    print(f"Done! Your Video is located under {path} \n")

elif choice == "2":
    print("Ok maybe later. \n")
    exit()

else:
    print("invalid input! \n")
    exit()