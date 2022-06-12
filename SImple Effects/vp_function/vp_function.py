import os
import cv2
import math
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
%matplotlib inline

REJECT_DEGREE_TH = 4.0

def FilterLines(Lines):
    FinalLines = []

    for Line in Lines:
        [[x1, y1, x2, y2]] = Line

        # Calculating equation of the line: y = mx + c
        if x1 != x2:
            m = (y2 - y1) / (x2 - x1)
        else:
            m = 100000000
        c = y2 - m*x2
        # theta will contain values between -90 -> +90.
        theta = math.degrees(math.atan(m))

        # Rejecting lines of slope near to 0 degree or 90 degree and storing others
        if REJECT_DEGREE_TH <= abs(theta) <= (90 - REJECT_DEGREE_TH):
            l = math.sqrt( (y2 - y1)**2 + (x2 - x1)**2 )    # length of the line
            FinalLines.append([x1, y1, x2, y2, m, c, l])

    if len(FinalLines) > 15:
        FinalLines = sorted(FinalLines, key=lambda x: x[-1], reverse=True)
        FinalLines = FinalLines[:15]

    return FinalLines

def GetLines(Image):
    GrayImage = cv2.cvtColor(Image, cv2.COLOR_BGR2GRAY)
    BlurGrayImage = cv2.GaussianBlur(GrayImage, (5, 5), 1)
    EdgeImage = cv2.Canny(BlurGrayImage, 40, 255)

    Lines = cv2.HoughLinesP(EdgeImage, 1, np.pi/180, 50, 10, 15)
    if Lines is None: exit(0)

    # Filtering Lines wrt angle
    FilteredLines = FilterLines(Lines)

    return FilteredLines

def GetVanishingPoint(Lines):
    VanishingPoint = None
    MinError = 100000000000
    for i in range(len(Lines)):
        for j in range(i+1, len(Lines)):
            m1, c1 = Lines[i][4], Lines[i][5]
            m2, c2 = Lines[j][4], Lines[j][5]
            if m1 != m2:
                x0 = (c1 - c2) / (m2 - m1)
                y0 = m1 * x0 + c1
                err = 0
                for k in range(len(Lines)):
                    m, c = Lines[k][4], Lines[k][5]
                    m_ = (-1 / m)
                    c_ = y0 - m_ * x0
                    x_ = (c - c_) / (m_ - m)
                    y_ = m_ * x_ + c_
                    l = math.sqrt((y_ - y0)**2 + (x_ - x0)**2)
                    err += l**2
                err = math.sqrt(err)

                if MinError > err:
                    MinError = err
                    VanishingPoint = [x0, y0]

    return VanishingPoint

def render_text(text):
    ttf = '/content/Arial.ttf'
    W, H = (450, 150)
    font = ImageFont.truetype(ttf, 100)

    wm = Image.new('RGBA',(W,H),(0,0,0,0))
    im = Image.new('RGBA',(W,H),(0,0,0,0))

    draw = ImageDraw.Draw(wm)
    w,h = draw.textsize(text, font)
    draw.text((0,0),text,(255,255,255),font)

    en = ImageEnhance.Brightness(wm)
    #en.putalpha(mask)
    mask = en.enhance(0.1)
    im.paste(wm,(25,25),mask)
    im.save('text.png')

    perspec_arr = [[33,44], [w+18,44], [33,h+25], [w+18,h+25]]
    return perspec_arr

def render_lines(origin_pic):
    GrayImage = cv2.cvtColor(origin_pic, cv2.COLOR_BGR2GRAY)
    BlurGrayImage = cv2.GaussianBlur(GrayImage, (5, 5), 1)
    EdgeImage = cv2.Canny(BlurGrayImage, 40, 255)
    Lines = cv2.HoughLinesP(EdgeImage, 1, np.pi/180, 50, 20, 15)
    return Lines

def render_vp(origin_pic):
    getlines = GetLines(origin_pic)
    VanishingPoint = GetVanishingPoint(getlines)
    v1 = int(VanishingPoint[0])
    v2 = int(VanishingPoint[1])
    return [v1,v2]

def img_process(img_index, perspec_arr, pts, text_img, z, n, k):
    org = np.float32(perspec_arr) # origin
    trans = np.float32(pts) # transformed
    M = cv2.getPerspectiveTransform(org, trans)
    perspec = cv2.warpPerspective(text_img, M, (600,600))
    cv2.imwrite("perspec.jpg", perspec)

    img = Image.open('perspec.jpg')
    rgba = img.convert("RGBA")
    datas = rgba.getdata()

    newData = []
    for item in datas:
        if item[0] < 160 and item[1] < 160 and item[2] < 160:
            # replacing it with a transparent value
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
        rgba.putdata(newData)
        rgba.save("transparent.png")

        background = Image.open('/content/origin_pic/pic' + str(img_index) + '.jpg')
        foreground = Image.open("transparent.png")
        x,y = foreground.size
        background.paste(foreground, (0, 0, x, y), foreground)
        if z==0:  background.save('/content/images/' + str(k) + '.png')
        else: background.save('/content/images/' + str(n+k) + '.png')
    return

def create_video(n):
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    video = cv2.VideoWriter('video.mp4', fourcc, 60, (600, 600))

    # Appending the images to the video one by one
    if n==350:
        for i in range(n):
            image = cv2.imread('/content/images/'+str(i)+'.png')
            video.write(image)
    else:
        for i in range(n*2):
            image = cv2.imread('/content/images/'+str(i)+'.png')
            video.write(image)

        video.release()
    return

index_arr = [
              [[169, 17], [153, 54]],
              [[84, 10], [111, 102]],
              [[49,85], [31,59]],
              [[62, 16], [24, 39]],
              [[41, 83], [37, 5]],
              [[13, 31], [3, 44]],
              [[18,41], [27,27]],
              [[1, 1], [6, 6]],
              [[46, 46], [48, 48]],
              [[13,13], [-1,-1]]
             ]

def VP(img_index, enter_text):
    img_index = int(img_index)
    origin_pic = cv2.imread('/content/origin_pic/pic' + str(img_index) + '.jpg')

    perspec_arr = render_text(enter_text)
    Lines = render_lines(origin_pic)
    v1 = render_vp(origin_pic)[0]
    v2 = render_vp(origin_pic)[1]

    ##### IMG + TEXT #####
    text_img = cv2.imread("/content/text.png", cv2.IMREAD_UNCHANGED)

    if img_index==10: n = 350
    else: n = 100

    if img_index <= 3:
        for z in range(2):
            index = index_arr[img_index-1]
            for k in range(n):
                x = [ [50+k,150+k], [340+k,440+k] ]
                pts = []
                for i in index[z]:
                    m = (v2 - Lines[i][0][1]) / (v1 - Lines[i][0][0])
                    c = v2 - m*v1
                    pts.append([int(x[z][0]), int(m*x[z][0]+c)])
                    pts.append([int(x[z][1]), int(m*x[z][1]+c)])
                img_process(img_index, perspec_arr, pts, text_img, z, n, k)

    elif img_index == 4:
        for z in range(2):
            index = index_arr[img_index-1]
            for k in range(n):
                x = [ [50+k,150+k], [340+k,440+k] ]
                pts = []
                ccount = 0
                for i in index[z]:
                    m = (v2 - Lines[i][0][1]) / (v1 - Lines[i][0][0])
                    c = v2 - m*v1
                    if ccount==0: c+=50
                    pts.append([int(x[z][0]), int(m*x[z][0]+c)])
                    pts.append([int(x[z][1]), int(m*x[z][1]+c)])
                    ccount = 1
                img_process(img_index, perspec_arr, pts, text_img, z, n, k)

    elif img_index == 5:
        for z in range(2):
            index = index_arr[img_index-1]
            for k in range(n):
                x = [  [100+k,200+k], [400+k,500+k] ]
                pts = []
                for i in index[z]:
                    m = (v2 - Lines[i][0][1]) / (v1 - Lines[i][0][0])
                    c = v2 - m*v1
                    pts.append([int(x[z][0]), int(m*x[z][0]+c)])
                    pts.append([int(x[z][1]), int(m*x[z][1]+c)])
                img_process(img_index, perspec_arr, pts, text_img, z, n, k)

    elif img_index == 6:
        for z in range(2):
            index = index_arr[img_index-1]
            for k in range(n):
                x = [ [50+k,150+k], [340+k,440+k] ]
                pts = []
                ccount = 0
                for i in index[z]:
                    m = (v2 - Lines[i][0][1]) / (v1 - Lines[i][0][0])
                    c = v2 - m*v1
                    if ccount==0 and z==0: c+=50
                    pts.append([int(x[z][0]), int(m*x[z][0]+c)])
                    pts.append([int(x[z][1]), int(m*x[z][1]+c)])
                    ccount = 1
                img_process(img_index, perspec_arr, pts, text_img, z, n, k)

    elif img_index == 7:
        for z in range(2):
            index = index_arr[img_index-1]
            for k in range(n):
                x = [ [50+k,150+k], [340+k,440+k] ]
                pts = []
                ccount = 0
                for i in index[z]:
                    m = (v2 - Lines[i][0][1]) / (v1 - Lines[i][0][0])
                    if ccount==1 and z==1: m=m+1
                    c = v2 - m*v1
                    pts.append([int(x[z][0]), int(m*x[z][0]+c)])
                    pts.append([int(x[z][1]), int(m*x[z][1]+c)])
                    ccount = 1
                img_process(img_index, perspec_arr, pts, text_img, z, n, k)

    elif img_index == 8 or img_index == 9:
        for z in range(2):
            index = index_arr[img_index-1]
            for k in range(n):
                x = [ [50+k,150+k], [340+k,440+k] ]
                pts = []
                ccount = 0
                for i in index[z]:
                    m = (v2 - Lines[i][0][1]) / (v1 - Lines[i][0][0])
                    if ccount==0:
                        if z==0: m += 0.6
                        else: m -= 1
                    c = v2 - m*v1
                    pts.append([int(x[z][0]), int(m*x[z][0]+c)])
                    pts.append([int(x[z][1]), int(m*x[z][1]+c)])
                    ccount = 1
                img_process(img_index, perspec_arr, pts, text_img, z, n, k)

    else:
        z = 0
        index = index_arr[img_index-1]
        for k in range(n):
            x = [ [50+k,150+k], [340+k,440+k] ]
            pts = []
            ccount = 0
            for i in index[z]:
                m = (v2 - Lines[i][0][1]) / (v1 - Lines[i][0][0])
                if ccount==0: m += 0.6
                c = v2 - m*v1
                pts.append([int(x[z][0]), int(m*x[z][0]+c)])
                pts.append([int(x[z][1]), int(m*x[z][1]+c)])
                ccount = 1
            img_process(img_index, perspec_arr, pts, text_img, z, n, k)

    create_video(n)

    return

if __name__ == '__main__':
    img_index = input()
    enter_text = input()
    VP(img_index, enter_text)
