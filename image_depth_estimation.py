import cv2
import torch
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as _img
import os
from PIL import Image, ImageDraw, ImageFont

def depth_estimation(file_path):
    model_type = "DPT_Large"     # MiDaS v3 - Large     (highest accuracy, slowest inference speed)
    # model_type = "DPT_Hybrid"   # MiDaS v3 - Hybrid    (medium accuracy, medium inference speed)
    # model_type = "MiDaS_small"  # MiDaS v2.1 - Small   (lowest accuracy, highest inference speed)
    midas = torch.hub.load("intel-isl/MiDaS", model_type)

    device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
    midas.to(device)
    midas.eval()

    midas_transforms = torch.hub.load("intel-isl/MiDaS", "transforms")
    if model_type == "DPT_Large" or model_type == "DPT_Hybrid":
        transform = midas_transforms.dpt_transform
    else:
        transform = midas_transforms.small_transform

    ##### resize #####
    img = cv2.imread(file_path)
    h, w = img.shape[0], img.shape[1]
    img = cv2.resize(img, (int(w), int(h)), interpolation=cv2.INTER_AREA)
    input_batch = transform(img).to(device)

    with torch.no_grad():
        prediction = midas(input_batch)
        print(prediction)
        prediction_filter = torch.nn.functional.interpolate(
            prediction.unsqueeze(1),
            size=img.shape[:2],
            mode="bicubic",
            align_corners=False,
        ).squeeze()
    output = prediction_filter.cpu().numpy()

    plt.imshow(output)
    plt.show()

    return output

def effect_text_move():
    georgia_bold_italic = 'I.Ngaan.ttf'
    txt = input("input text: ")
    txt_len = len(txt)
    background = (0,0,0) # white
    fontsize = 24
    W, H = (fontsize*txt_len, fontsize) # image size
    font = ImageFont.truetype(georgia_bold_italic, fontsize)
    image = Image.new('RGBA', (W, H), background)
    draw = ImageDraw.Draw(image)
    w, h = font.getsize(txt)
    draw.text(((W-w)/2,(H-h)/2), txt, fill='lime', font=font)
    save_location = os.getcwd()
    image.save(save_location + '/sample.png')

    text_img = Image.open('sample.png')
    rgba = text_img.convert("RGBA")
    datas = rgba.getdata()
    newData = []
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:  # finding black colour by its RGB value
            # storing a transparent value when we find a black colour
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)  # other colours remain unchanged

    rgba.putdata(newData)
    rgba.save("transparent_image.png", "PNG")

    frontimage_path = 'transparent_image.png'
    frontimg = cv2.imread(frontimage_path, cv2.IMREAD_UNCHANGED)
    h, w = frontimg.shape[0], frontimg.shape[1]
    frontimg = cv2.resize(frontimg, (int(w), int(h)), interpolation=cv2.INTER_AREA)
    print(frontimg.shape)
    # frontimg = cv2.cvtColor(frontimg, cv2.COLOR_BGR2BGRA)
    return frontimg




if __name__ == '__main__':
    depth_estimation('pets.jpg')
    # effect_text_move()
    # print('Finished')



@article{Ranftl2020,
	author    = {Ren\'{e} Ranftl and Katrin Lasinger and David Hafner and Konrad Schindler and Vladlen Koltun},
	title     = {Towards Robust Monocular Depth Estimation: Mixing Datasets for Zero-shot Cross-dataset Transfer},
	journal   = {IEEE Transactions on Pattern Analysis and Machine Intelligence (TPAMI)},
	year      = {2020},
}
@article{Ranftl2021,
	author    = {Ren\'{e} Ranftl and Alexey Bochkovskiy and Vladlen Koltun},
	title     = {Vision Transformers for Dense Prediction},
	journal   = {ArXiv preprint},
	year      = {2021},
}

