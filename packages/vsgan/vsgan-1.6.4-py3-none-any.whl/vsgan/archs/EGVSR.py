import functools

import numpy as np
import torch
import torch.nn as nn
# noinspection PyPep8Naming
import torch.nn.functional as F
from torch import Tensor

from vsgan.constants import STATE_T


class EGVSR(nn.Module):
    """
    EGVSR - Efficient & Generic Video Super-Resolution.
    By Yanpeng Cao, Chengcheng Wang, Changjun Song, Yongming Tang, and He Li.
    """

    def __init__(self, model: str, scale=4, in_nc=3, out_nc=3, nf=64, nb=16, degradation="BI") -> None:
        super(EGVSR, self).__init__()

        self.model = model
        self.state: STATE_T = torch.load(self.model)
        self.in_nc = in_nc
        self.out_nc = out_nc
        self.scale = scale
        self.num_filters = nf
        self.num_blocks = nb

        self.upsample_func = {
            "BI": functools.partial(F.interpolate, scale_factor=scale, mode="bilinear", align_corners=False),
            "BD": BicubicUpsample(scale_factor=scale)
        }.get(degradation)
        if self.upsample_func is None:
            raise NotImplementedError("Degradation [%s] is not recognized" % degradation)

        self.fnet = FNet(in_nc)
        self.srnet = SRNet(in_nc, out_nc, nf, nb, self.upsample_func)

        self.load_state_dict(self.state, strict=False)

    def forward(self, lr_curr, lr_prev, hr_prev):
        """
        Args:
            lr_curr: the current lr data in shape NCHW
            lr_prev: the previous lr data in shape NCHW
            hr_prev: the previous hr data in shape NC(4H)(4W)
        """

        # estimate lr flow (lr_curr -> lr_prev)
        lr_flow = self.fnet(lr_curr, lr_prev)

        # pad if size is not a multiple of 8
        pad_h = lr_curr.size(2) - lr_curr.size(2) // 8 * 8
        pad_w = lr_curr.size(3) - lr_curr.size(3) // 8 * 8
        lr_flow_pad = F.pad(lr_flow, (0, pad_w, 0, pad_h), 'reflect')

        # upsample lr flow
        hr_flow = self.scale * self.upsample_func(lr_flow_pad)

        # warp hr_prev
        hr_prev_warp = backward_warp(hr_prev, hr_flow)

        # compute hr_curr
        hr_curr = self.srnet(lr_curr, space_to_depth(hr_prev_warp, self.scale))

        return hr_curr

    def forward_sequence(self, lr_data: Tensor):
        """
        Args:
            lr_data: lr data in shape NTCHW
        """

        n, t, c, lr_h, lr_w = lr_data.size()
        hr_h, hr_w = lr_h * self.scale, lr_w * self.scale

        # calculate optical flows
        lr_prev = lr_data[:, :-1, ...].reshape(n * (t - 1), c, lr_h, lr_w)
        lr_curr = lr_data[:, 1:, ...].reshape(n * (t - 1), c, lr_h, lr_w)
        lr_flow = self.fnet(lr_curr, lr_prev)  # n*(t-1),2,h,w

        # upsample lr flows
        hr_flow = self.scale * self.upsample_func(lr_flow)
        hr_flow = hr_flow.view(n, (t - 1), 2, hr_h, hr_w)

        # compute the first hr data
        hr_data = []
        hr_prev = self.srnet(
            lr_data[:, 0, ...],
            torch.zeros(
                n, (self.scale ** 2) * c, lr_h, lr_w,
                dtype=lr_data.dtype,
                device=lr_data.device
            )
        )
        hr_data.append(hr_prev)

        # compute the remaining hr data
        for i in range(1, t):
            # warp hr_prev
            hr_prev_warp = backward_warp(hr_prev, hr_flow[:, i - 1, ...])

            # compute hr_curr
            hr_curr = self.srnet(
                lr_data[:, i, ...],
                space_to_depth(hr_prev_warp, self.scale)
            )

            # save and update
            hr_data.append(hr_curr)
            hr_prev = hr_curr

        hr_data = torch.stack(hr_data, dim=1)  # n,t,c,hr_h,hr_w

        # construct output dict
        """
        ret_dict = {
            'hr_data': hr_data,  # n,t,c,hr_h,hr_w
            'hr_flow': hr_flow,  # n,t,2,hr_h,hr_w
            'lr_prev': lr_prev,  # n(t-1),c,lr_h,lr_w
            'lr_curr': lr_curr,  # n(t-1),c,lr_h,lr_w
            'lr_flow': lr_flow,  # n(t-1),2,lr_h,lr_w
        }
        return ret_dict
        """
        return hr_data, hr_flow, lr_prev, lr_curr, lr_flow


class FNet(nn.Module):
    """Optical flow estimation network."""

    def __init__(self, in_nc: int):
        super(FNet, self).__init__()

        self.encoder1 = nn.Sequential(
            nn.Conv2d(2 * in_nc, 32, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(32, 32, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.MaxPool2d(2, 2))

        self.encoder2 = nn.Sequential(
            nn.Conv2d(32, 64, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, 64, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.MaxPool2d(2, 2))

        self.encoder3 = nn.Sequential(
            nn.Conv2d(64, 128, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(128, 128, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.MaxPool2d(2, 2))

        self.decoder1 = nn.Sequential(
            nn.Conv2d(128, 256, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(256, 256, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True))

        self.decoder2 = nn.Sequential(
            nn.Conv2d(256, 128, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(128, 128, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True))

        self.decoder3 = nn.Sequential(
            nn.Conv2d(128, 64, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(64, 64, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True))

        self.flow = nn.Sequential(
            nn.Conv2d(64, 32, 3, 1, 1, bias=True),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(32, 2, 3, 1, 1, bias=True))

    def forward(self, x1, x2):
        """Compute optical flow from x1 to x2."""
        out = self.encoder1(torch.cat([x1, x2], dim=1))
        out = self.encoder2(out)
        out = self.encoder3(out)
        out = F.interpolate(self.decoder1(out), scale_factor=2, mode='bilinear', align_corners=False)
        out = F.interpolate(self.decoder2(out), scale_factor=2, mode='bilinear', align_corners=False)
        out = F.interpolate(self.decoder3(out), scale_factor=2, mode='bilinear', align_corners=False)
        out = torch.tanh(self.flow(out)) * 24  # 24 is the max velocity
        return out


class SRNet(nn.Module):
    """Reconstruction and Upsampling network."""

    def __init__(self, in_nc: int = 3, out_nc: int = 3, nf: int = 64, nb: int = 16, upsample_func=None, scale: int = 4):
        super(SRNet, self).__init__()

        # input conv.
        self.conv_in = nn.Sequential(
            nn.Conv2d((scale ** 2 + 1) * in_nc, nf, 3, 1, 1, bias=True),
            nn.ReLU(inplace=True))

        # residual blocks
        self.resblocks = nn.Sequential(*[ResidualBlock(nf) for _ in range(nb)])

        # upsampling
        self.conv_up = nn.Sequential(
            nn.ConvTranspose2d(nf, nf, 3, 2, 1, output_padding=1, bias=True),
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(nf, nf, 3, 2, 1, output_padding=1, bias=True),
            nn.ReLU(inplace=True))

        self.conv_up_cheap = nn.Sequential(
            nn.PixelShuffle(4),
            nn.ReLU(inplace=True))

        # output conv.
        self.conv_out = nn.Conv2d(4, out_nc, 3, 1, 1, bias=True)

        # upsampling function
        self.upsample_func = upsample_func

    def forward(self, lr_curr, hr_prev_tran):
        """ lr_curr: the current lr data in shape nchw
            hr_prev_tran: the previous transformed hr_data in shape n(4*4*c)hw
        """

        out = self.conv_in(torch.cat([lr_curr, hr_prev_tran], dim=1))
        out = self.resblocks(out)
        out = self.conv_up_cheap(out)
        out = self.conv_out(out)
        # out += self.upsample_func(lr_curr)

        return out


class ResidualBlock(nn.Module):
    """Residual block without batch normalization."""

    def __init__(self, nf: int = 64):
        super(ResidualBlock, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(nf, nf, 3, 1, 1, bias=True),
            nn.ReLU(inplace=True),
            nn.Conv2d(nf, nf, 3, 1, 1, bias=True)
        )

    def forward(self, x):
        return self.conv(x) + x


class BicubicUpsample(nn.Module):
    """
    A bicubic upsampling class with similar behavior to that in TecoGAN-Tensorflow.

    Note that it's different from torch.nn.functional.interpolate and matlab's
    imresize in terms of bicubic kernel and sampling scheme.

    Theoretically it can support any scale_factor >= 1, but currently only
    scale_factor = 4 is tested.

    References:
        http://verona.fi-p.unam.mx/boris/practicas/CubConvInterp.pdf
        https://stackoverflow.com/q/26823140/13183782
    """

    def __init__(self, scale_factor, a=-0.75):
        super(BicubicUpsample, self).__init__()

        # calculate weights
        cubic = torch.FloatTensor([
            [0, a, -2 * a, a],
            [1, 0, -(a + 3), a + 2],
            [0, -a, (2 * a + 3), -(a + 2)],
            [0, 0, a, -a]
        ])  # accord to Eq.(6) in the reference paper

        kernels = [
            torch.matmul(cubic, torch.FloatTensor([1, s, s ** 2, s ** 3]))
            for s in [1.0 * d / scale_factor for d in range(scale_factor)]
        ]  # s = x - floor(x)

        # register parameters
        self.scale_factor = scale_factor
        self.register_buffer('kernels', torch.stack(kernels))

    def forward(self, input):
        n, c, h, w = input.size()
        s = self.scale_factor

        # pad input (left, right, top, bottom)
        input = F.pad(input, (1, 2, 1, 2), mode='replicate')

        # calculate output (height)
        kernel_h = self.kernels.repeat(c, 1).view(-1, 1, s, 1)
        output = F.conv2d(input, kernel_h, stride=1, padding=0, groups=c)
        output = output.reshape(
            n, c, s, -1, w + 3).permute(0, 1, 3, 2, 4).reshape(n, c, -1, w + 3)

        # calculate output (width)
        kernel_w = self.kernels.repeat(c, 1).view(-1, 1, 1, s)
        output = F.conv2d(output, kernel_w, stride=1, padding=0, groups=c)
        output = output.reshape(
            n, c, s, h * s, -1).permute(0, 1, 3, 4, 2).reshape(n, c, h * s, -1)

        return output


def backward_warp(x: Tensor, flow: Tensor, mode: str = "bilinear", padding_mode: str = "border") -> Tensor:
    """
    Backward warp `x` according to `flow`.
    Both x and flow are pytorch tensor in shape `nchw` and `n2hw`.
    Reference:
        https://github.com/sniklaus/pytorch-spynet/blob/master/run.py#L41
    """

    n, c, h, w = x.size()

    # create mesh grid
    iu = torch.linspace(-1.0, 1.0, w).view(1, 1, 1, w).expand(n, -1, h, -1).type_as(flow)
    iv = torch.linspace(-1.0, 1.0, h).view(1, 1, h, 1).expand(n, -1, -1, w).type_as(flow)
    grid = torch.cat([iu, iv], 1).to(flow.device)

    # normalize flow to [-1, 1]
    flow = torch.cat([
        flow[:, 0:1, ...] / ((w - 1.0) / 2.0),
        flow[:, 1:2, ...] / ((h - 1.0) / 2.0)], dim=1)

    # add flow to grid and reshape to nhw2
    grid = (grid + flow).permute(0, 2, 3, 1)

    # bilinear sampling
    output = F.grid_sample(x, grid, mode=mode, padding_mode=padding_mode, align_corners=True)

    return output


def space_to_depth(x: Tensor, scale: int = 4) -> Tensor:
    """Equivalent to tf.space_to_depth()."""
    n, c, in_h, in_w = x.size()
    out_h, out_w = in_h // scale, in_w // scale

    x_reshaped = x.reshape(n, c, out_h, scale, out_w, scale)
    x_reshaped = x_reshaped.permute(0, 3, 5, 1, 2, 4)
    output = x_reshaped.reshape(n, scale * scale * c, out_h, out_w)

    return output


def float32_to_uint8(array: np.ndarray) -> np.ndarray:
    """
    Convert np.float32 array to np.uint8.

    Args:
        array: np.float32, (NT)CHW, [0, 1]

    Returns:
        np.uint8, (NT)CHW, [0, 255]
    """
    return np.uint8(np.clip(np.round(array * 255), 0, 255))
