from PIL import Image
def save_tensor_as_img(xim, i):
    H, W = xim.shape[-2:]
    arr = xim[i].detach().cpu().numpy()
    m1 = arr.max()
    m2 = arr.min()
    arr = (arr - m2) / (m1 - m2 ) * 255
    im = Image.fromarray(arr).convert("RGB")
    im.save(f"data/images/x{i}_{H}_{W}.png")
    print(f"{i}_{H}_{W} max: {m1:.2f} {m2:.2f}")

def save_tensor_as_img_simple(xim, i):
    H, W = xim.shape[-2:]
    arr = xim.detach().cpu().numpy()
    arr = arr / arr.max() * 255
    im = Image.fromarray(arr).convert("RGB")
    im.save(f"data/images/x{i}_{H}_{W}.png")
    print(f"{i}_{H}_{W}")

import numpy as np

def save_tensor(xim):
    """xim: T[3, h, w]"""
    H, W = xim.shape[-2:]
    arr = xim.detach().cpu().permute(1, 2, 0).numpy()
    m1 = arr.max()
    m2 = arr.min()
    arr = (arr - m2) / (m1 - m2 ) * 255
    arr = arr.astype(np.uint8)
    im = Image.fromarray(arr)
    im.save(f"data/images/x_{H}_{W}.png")
    print(f"{H}_{W} max: {m1:.2f} {m2:.2f}")
    return im
import torch
import cv2
def save_heatmap(features, scale=8):
    # 1.1 获取feature maps
    # features = ...  # 尺度大小，如：torch.Size([1,80,45,45])
    # 1.2 每个通道对应元素求和
    assert features.ndim == 3
    heatmap = torch.sum(features, dim=0)  # 尺度大小， 如torch.Size([1,45,45])
    size = features.shape[1:]  # 原图尺寸大小
    src_size = (size[1] * scale, size[0] * scale)
    max_value = torch.max(heatmap)
    min_value = torch.min(heatmap)
    heatmap = (heatmap-min_value) / (max_value-min_value) * 255
    heatmap = heatmap.detach().cpu().numpy().astype(np.uint8) # .transpose(1,2,0)  # 尺寸大小，如：(45, 45, 1)
    heatmap = cv2.resize(heatmap, src_size, interpolation=cv2.INTER_LINEAR)  # 重整图片到原尺寸
    heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET) # H W C
    # 保存热力图
    im = Image.fromarray(heatmap)
    im.save(f"data/images/xh_{src_size[1]}_{src_size[0]}.png")
    print(f"{src_size[1]}_{src_size[0]} max: {max_value:.2f} {min_value:.2f}")
    return heatmap

def mix_heatmap(features, scale=8, hmratio=0.75):
    heatmap = save_heatmap(features, scale)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_RGB2BGR)
    
    src_size = heatmap.shape
    rawim = f"data/images/x_{src_size[0]}_{src_size[1]}.png"
    if not osp.exists(rawim):
        print("Not exist", rawim)
        return
    rawim = cv2.imread(rawim)
    superimposed_img = heatmap * hmratio + rawim * (1-hmratio)
    cv2.imwrite(f"data/images/mix_{src_size[0]}_{src_size[1]}.png", superimposed_img)

