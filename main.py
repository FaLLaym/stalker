from PIL import Image, ImageDraw
import math

import requests
import json


def get_intercetions(x0, y0, r0, x1, y1, r1):
    d=math.sqrt((x1-x0)**2 + (y1-y0)**2)
    # non intersecting
    if d > r0 + r1 :
        return None
    # One circle within other
    if d < abs(r0-r1):
        return None
    # coincident circles
    if d == 0 and r0 == r1:
        return None
    else:
        a=(r0**2-r1**2+d**2)/(2*d)
        h=math.sqrt(r0**2-a**2)
        x2=x0+a*(x1-x0)/d
        y2=y0+a*(y1-y0)/d
        x3=x2+h*(y1-y0)/d
        y3=y2-h*(x1-x0)/d

        x4=x2-h*(y1-y0)/d
        y4=y2+h*(x1-x0)/d

        return [[x3, y3], [x4, y4]]

def check(x, y, r, xc, yc):
    return ((x - xc)**2 + (y - yc)**2) < r**2

def get_point():
    res = []
    anim = []
    url = "https://dt.miet.ru/ppo_it_final"
    hed = {"X-Auth-Token": "uerzymvj"}
    a = requests.get(url, headers=hed)
    mas = json.loads(a.text)["message"]
    anom = {}
    for stan in mas:
        for point in stan["swans"]:
            if point["id"] not in anom:
                anom[point["id"]] = [[stan["coords"], point["rate"]]]
                anim += [point["id"]]
            else:
                anom[point["id"]] += [[stan["coords"], point["rate"]]]

    po = []
    for an in anim:
        for kof in range(10000):
            circl = []
            for i in anom[an]:
                circl.append(i[0]+[kof/i[1]])

            if len(circl) != 3:
                circl.pop(-1)
            for i in range(len(circl)):
                try:
                    if i+1 > len(circl):
                        po += get_intercetions(circl[i][0], circl[i][1], circl[i][2], circl[i+1][0], circl[i+1][1], circl[i+1][2])
                    else:
                        po += get_intercetions(circl[i][0], circl[i][1], circl[i][2], circl[-1][0], circl[-1][1], circl[-1][2])
                except Exception:
                    pass
            r = []
            rad = 0
            for p in po:
                k = 0
                for c in circl:
                    if check(p[0], p[1],c[2], c[0], c[1]):
                        k += 1
                        if rad == 0:
                            dist = math.hypot(c[0] - p[0], c[1] - c[1])
                            intes = c[2]
                            mx = intes*dist**2
                            for ra in range(1, 10000):
                                if mx / ra ** 2 < 3.1:
                                    rad = ra
                                    break
                if k>=3:
                    r += p
            if len(r)>0:
                res += [[r[0], r[1], ra/kof]]
                break
    return res

image = Image.open('map.png')
draw = ImageDraw.Draw(image)  # рисовалка
x, y = image.size
for i in get_point():
    x3 = i[0]
    y3 = i[1]
    r3 = i[2]
    r4 = r3 * 1.5
    position1 = x3 * 50
    position2 = y3 * 50
    eX = r3 * 50
    eY = r3 * 50
    eX2 = r4 * 50
    eY2 = r4 * 50
    box = (position1 - eX, position2 - eY, position1 + eX, position2 + eY)
    box2 = (position1 - eX2, position2 - eY2, position1 + eX2, position2 + eY2)



    draw.ellipse(box2, 'green', 'black')

    draw.ellipse(box, 'red', 'black')  # отрисовка окружность


    draw.point((x3, y3), fill='black')

m = image.save('map1.png')

