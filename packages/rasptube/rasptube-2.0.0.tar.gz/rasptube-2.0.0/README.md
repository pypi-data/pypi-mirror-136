# Rasptube
The Rasptube Python module was created by Walter J Hare to automate the tedious process of making a video compatable with the Raspberry Pi. It can be installed by running the command: 'pip3 install rasptube'. Rasptube runs on Python 3, it also requires that Python Module OS is installed to work.
# Linkgen
Linkgen generates the link by using the OS Python Module to run the command: 'sudo youtube-dl -g -f 22 "<URL>"'. It requires that you supply the URL of the video as a paramater, it also requires that you have Youtube-DL installed.
#Videoplayer
Videoplayer plays the video by using the OS Python Module to run the command: 'omxplayer -b "<URL>"'. It requires that you supply the the URL of the video as a paramater to work, it also requires that you have OMXPlayer installed. WARNING: Do not use a bluetooth keyboard.
