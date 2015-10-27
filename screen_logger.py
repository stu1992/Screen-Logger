from PIL import Image, ImageDraw
import sys
import time
import os
import commands
import logging
buffer = 15 # snapshots taken at 15 seconsd intervals
motionblur = buffer * 7 # number of previous snapshots mouse movements to hold

log = logging.getLogger()
logging.basicConfig()
log.setLevel(logging.ERROR)

def __main__():
    # open last timestamp
    try: #try to read last temp stamp
        last = open("time","r")
        tempstamp = int(last.read())
    except: # on fail assing it 1
        tempstamp = 1
    finally: # open file to keep track of new tempstamp
        last = open("time","w")

    log.info(str(tempstamp) + " read in")

    while True:
        time.sleep(buffer)
        # process previous picture from tempstamp
        try:
            background = Image.open("/home/stu/desktop/images/{}.png".format(tempstamp)) # open last image
            img = Image.new('RGBA', (1366, 768), (255, 255, 255, 0))
            log.info("{} opened for editing".format(tempstamp))
            pixdata = img.load()
            draw = ImageDraw.Draw(img)
            os.system('tail /var/log/mouse_log -n 10000 > /var/log/temp_mouse_log')
            mousedata = open('/var/log/temp_mouse_log','r') # mouse data file, ensure that mouse_log_no_args is running
            x1 = -1
            y1 = -1
            for line in mousedata.readlines():
                formatted = line.split()
                if len(formatted) != 4:
                    continue
                if int(formatted[0]) in range(int(tempstamp-motionblur),int(tempstamp+buffer)): #checking if timestamp is within buffer boundary
                    if x1 == -1 or y1 == -1:
                        x1 = int(formatted[2])
                        y1 = int(formatted[3])
                        log.debug('X1 initial value ' + str(x1))
                        continue
                    x2 = int(formatted[2])
                    y2 = int(formatted[3])
                    # making previous lines grey and recent ones black
                    #check if left mouse button was clicked
                    if int(formatted[1]) == 9:
                        draw.ellipse((x2-4, y2-5, x2+5, y2+5), fill=(255,100,100,128))
                    elif int(formatted[1]) == 10:
                        draw.ellipse((x2-5, y2-5, x2+5, y2+5), fill=(100,100,255,128))
                    elif int(formatted[1]) == 12:
                        draw.ellipse((x2-5, y2-5, x2+5, y2+5), fill=(100,255,100,128))
                    if int(formatted[0]) in range(int(tempstamp-motionblur), int(tempstamp)):
                        draw.line((x1,y1,x2,y2),fill=(0,0,0,128), width=3)
                    else:                    
                        draw.line((x1,y1,x2,y2),fill=(0,0,0,250), width=3)
                    x1 = x2
                    y1 = y2
            background.paste(img,(0,0), img)
            background.save("/home/stu/desktop/images/{}.png".format(tempstamp))
            log.info("edit saved as " +str(tempstamp)+".png")
        except Exception,e: log.error(str(e))

        timestamp = int(time.time())
        if timestamp in range(tempstamp + buffer-1,tempstamp + buffer+2): # tests for timestamp in +- 1 from 5 seconds from last screen shot
            os.system("scrot /home/stu/desktop/images/{}.png".format(timestamp))
            tempstamp = timestamp
        else:
            os.system("cp /home/stu/desktop/blank.png /home/stu/desktop/images/{}.png".format(timestamp))
            log.debug("timestamp: "+str(timestamp))
            log.debug("tempstamp: "+str(tempstamp))
            tempstamp = timestamp
        # finally persist timestamp
        last.seek(0)
        last.write(str(timestamp))
        #check if enough pictures have accumulated
        if getscreencount() >= 720:
            export()

def getscreencount(): # returns the number of files in the images folder
    images = commands.getoutput('ls /home/stu/desktop/images/')
    return len(images.split())
def export(): # renames the files in images to consecutive integers, exports a video file to videos and deletes images
    log.info('exporting video')
    images = commands.getoutput('ls /home/stu/desktop/images/')
    imagelist = images.split()
    name = imagelist[0][:10]
    count = 1
    for image in imagelist:
        os.system('mv /home/stu/desktop/images/{}'.format(image) + ' /home/stu/desktop/images/{}.png'.format(count))
        count += 1
    os.system('ffmpeg -i /home/stu/desktop/images/%d.png -vcodec mpeg4 /home/stu/desktop/videos/{}.mp4'.format(name)) # was.avi
    count -=1
    while count > 0:
        os.system('rm /home/stu/desktop/images/{}.png'.format(count))
        count -=1

__main__()
