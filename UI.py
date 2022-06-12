from cProfile import label
from lib2to3.pgen2.token import LEFTSHIFT
from tkinter import *
from tkinter import filedialog
from PIL import ImageTk, Image
from image_depth_estimation import depth_estimation, effect_text_move
from vp_function import VP
import matplotlib.pyplot as plt
import numpy as np
from tkvideo import tkvideo
import cv2

class Layout:
    def __init__(self):
        self.window = Tk()
        self.frame1 = 0
        self.frame2 = 0
        self.L1 = 0

        self.check1 = False

        self.img_path = 0
        self.img = 0
        self.logo_img_path = 0
        self.logo_img = 0
        self.canvas = 0
        self.depth_map =0

        self.img_index = -1
    def UploadPhoto(self):
        self.img_path = filedialog.askopenfilename()
        print("Selected: ", self.img_path)

        self.img = cv2.imread(self.img_path)
        self.img = cv2.resize(self.img, (int(self.img.shape[1]), int(self.img.shape[0])), interpolation=cv2.INTER_AREA)
        print(self.img.shape)

        img = Image.open(self.img_path)
        img = img.resize((img.width, img.height))
        imgTk = ImageTk.PhotoImage(img)
        label = Label(self.frame1, image=imgTk)
        label.image = imgTk
        # label.pack(padx=20, pady=20, side=LEFT)
        label.pack()
    def GetDepthMap(self):
        self.depth_map = depth_estimation(self.img_path)
        print('Got Depth Image')
        plt.imshow(self.depth_map)
        print(self.depth_map.shape)
        # plt.show()
    def EffectFluid(self):
        tmp_depth = 0
        fourcc =cv2.VideoWriter_fourcc(*'XVID')
        output = cv2.VideoWriter('output_sample/effect_sample.avi', fourcc, 60, (600, 600))
        num_frame = 0
        while(True):
            img_tmp = self.img.copy()
            indices = np.where(self.depth_map < tmp_depth)
            # img_tmp[indices] = (255, 178, 236)
            colorimg = img_tmp.copy()
            colorimg[indices] = (119,84,0)
            #img_tmp[indices] = (3, 147, 5)
            lap = cv2.addWeighted(img_tmp, 0.7, colorimg, 0.3, 0.0)
            tmp_depth += 0.03

            output.write(lap)
            num_frame += 1
            if num_frame == 60*15:
                print("Finished")
                self.OutputSampleDsiplay()
                break

        #     cv2.imshow('output', img_tmp)
        #     if cv2.waitKey(10) & 0xFF == ord('q'):
        #         break
        # cv2.destroyAllWindows()
    def EffectTextMove(self):
        # self.ClearFrame(self.frame2)
        frontimg = effect_text_move()
        # img_tmp = img.copy()
        h, w = self.img.shape[0], self.img.shape[1]
        edge_x = frontimg.shape[0] - h
        edge_y = frontimg.shape[1] - w

        depth = 3
        x_offset = 0
        y_offset = 0
        x_offset_add = 1
        y_offset_add = 1
        fourcc =cv2.VideoWriter_fourcc(*'XVID')
        output = cv2.VideoWriter('output_sample/effect_sample.avi', fourcc, 60, (600, 600))
        num_frame = 0
        while True:
            # print(num_frame)
            img_tmp = self.img.copy()

            mask = img_tmp[x_offset:x_offset + frontimg.shape[0], y_offset:y_offset + frontimg.shape[1]].copy()

            indices = np.where(self.depth_map > depth)
            # print(indices)
            # print(frontimg)

            mask[frontimg[:, :, 3] > 0] = frontimg[frontimg[:, :, 3] > 0][:, 0:3]


            img_tmp[x_offset:x_offset + frontimg.shape[0], y_offset:y_offset + frontimg.shape[1]] = mask
            img_tmp[indices] = self.img[indices]

            if x_offset + frontimg.shape[0] >= h:
                x_offset_add = -1
            elif x_offset <= 0:
                x_offset_add = 1
            if y_offset + frontimg.shape[1] >= w:
                y_offset_add = -1
            elif y_offset <= 0:
                y_offset_add = 1

            x_offset += x_offset_add
            y_offset += y_offset_add

            output.write(img_tmp)

            num_frame += 1
            if num_frame == 60*10:
                print("Finished")
                self.OutputSampleDsiplay()
                break
    def test(self):
        self.check1 = True

    def EffectVanishedPoint(self):
        self.img_index = self.img_path.split(".")[0].split("/")[-1][-1]
        # var = StringVar()
        # w1 = Tk()
        # entry = Entry(w1, textvariable=var)
        # entry.pack()
        # b = Button(w1, text='ENTER', command=self.test)
        # b.pack(padx=0, pady=0, side=TOP)
        # w1.mainloop()
        enter_text = input("input text: ")
        self.VanishOutputSampleDsiplay(self.img_index)
        # print(img_index)
        # enter_text = input()
        # VP(img_index, enter_text)



    def OutputSampleDsiplay(self):
        label = Label(self.frame2)
        label.pack()
        player = tkvideo("output_sample/effect_sample.avi", label, loop = 10, size = (600,600))
        player.play()
    def VanishOutputSampleDsiplay(self, index):
        label = Label(self.frame2)
        label.pack()
        path = "vanish_output_sample/video" + str(index) + ".mp4"
        player = tkvideo(path, label, loop = 10, size = (600,600))
        player.play()

    def ClearFrame1(self):
        for w in self.frame1.winfo_children():
            w.destroy()
    def ClearFrame2(self):
        for w in self.frame2.winfo_children():
            w.destroy()



    def run(self):
        self.window.title('Simple Effects UI')
        self.window.geometry('1440x810')
        self.window.minsize(width=960, height=540)
        self.window.maxsize(width=1440, height=810)

        self.frame1 = Frame(width=600, height=600, relief=RAISED, border=5)
        self.frame1.pack(padx=5, pady=10, side=LEFT)
        self.frame2 = LabelFrame(width=600, height=600, relief=RAISED, border=5)
        self.frame2.pack(padx=60, pady=10, side=LEFT)

        # self.L1 = Label(self.frame2, height=600, width=600)
        # self.L1.pack(padx=60, pady=10)

        button1 = Button(self.window, text='Upload Photo', command=self.UploadPhoto)
        button1.pack(padx=0, pady=0, side=TOP)
        button2 = Button(self.window, text='Get Depth Map', command=self.GetDepthMap)
        button2.pack(padx=0, pady=0, side=TOP)
        button3 = Button(self.window, text='Efect Fluid', command=self.EffectFluid)
        button3.pack(padx=0, pady=0, side=TOP)
        button4 = Button(self.window, text='Effect Text Move', command=self.EffectTextMove)
        button4.pack(padx=0, pady=0, side=TOP)
        button5 = Button(self.window, text='Effect Vanish Point', command=self.EffectVanishedPoint)
        button5.pack(padx=0, pady=0, side=TOP)
        button6 = Button(self.window, text='Frame1 Clear', command=self.ClearFrame1)
        button6.pack(padx=0, pady=0, side=TOP)
        button7 = Button(self.window, text='Frame2 Clear', command=self.ClearFrame2)
        button7.pack(padx=0, pady=0, side=TOP)

if __name__ == '__main__':
    LY = Layout()
    LY.run()
    LY.window.mainloop()



