import collections
import hashlib
import math
import os
import random
import re
import shutil
import sys
import tarfile
import time
import zipfile
from collections import defaultdict

import pandas as pd
import requests
from IPython import display
from matplotlib import pyplot as plt
import numpy as np
import torch
import torchvision
from PIL import Image
from torch import nn
from torch.nn import functional as F
from torch.utils import data
from torchvision import transforms


#mylib = sys.modules[__name__]

def use_svg_display():
    # Use the svg format to display a plot in Jupyter.
    display.set_matplotlib_formats('svg')

def set_figsize(figsize=(3.5, 2.5)):
    # Set the figure size for matplotlib.
    use_svg_display()
    plt.rcParams['figure.figsize'] = figsize

def set_axes(axes, xlabel, ylabel, xlim, ylim, xscale, yscale, legend):
    # Set the axes for matplotlib.
    axes.set_xlabel(xlabel)
    axes.set_ylabel(ylabel)
    axes.set_xscale(xscale)
    axes.set_yscale(yscale)
    axes.set_xlim(xlim)
    axes.set_ylim(ylim)
    if legend:
        axes.legend(legend)
    axes.grid()#用于画网格线

def plot(X, Y=None, xlabel=None, ylabel=None, legend=None, xlim=None,
         ylim=None, xscale='linear', yscale='linear',
         fmts=('-', 'm--', 'g-.', 'r:'), figsize=(3.5, 2.5), axes=None):

    if legend is None:
        legend = []

    set_figsize(figsize)
    axes = axes if axes else plt.gca()

    # Return True if `X` (tensor or list) has 1 axis
    def has_one_axis(X):
        return (hasattr(X, "ndim") and X.ndim == 1 or isinstance(X, list)
                and not hasattr(X[0], "__len__"))

    if has_one_axis(X):
        X = [X]
    if Y is None:
        X, Y = [[]] * len(X), X
    elif has_one_axis(Y):
        Y = [Y]
    if len(X) != len(Y):
        X = X * len(Y)
    axes.cla()
    for x, y, fmt in zip(X, Y, fmts):
        if len(x):
            axes.plot(x, y, fmt)
        else:
            axes.plot(y, fmt)
    set_axes(axes, xlabel, ylabel, xlim, ylim, xscale, yscale, legend)


class Logger(object):
    def __init__(self,fileN ="Default.log"):
        self.terminal = sys.stdout
        self.log = open(fileN,"a")
 
    def write(self,message):
        self.terminal.write(message)
        self.log.write(message)
 
    def flush(self):
        pass


class Timer:
    """Record multiple running times."""
    def __init__(self):
        self.times = []
        self.start()

    def start(self):
        """Start the timer."""
        self.tik = time.time()

    def stop(self):
        """Stop the timer and record the time in a list."""
        self.times.append(time.time() - self.tik)
        return self.times[-1]

    def avg(self):
        """Return the average time."""
        return sum(self.times) / len(self.times)

    def sum(self):
        """Return the sum of time."""
        return sum(self.times)

    def cumsum(self):
        """Return the accumulated time."""
        return np.array(self.times).cumsum().tolist()

def synthetic_data(w, b, num_examples):
    X = torch.normal(0, 1, (num_examples, len(w)))
    y = torch.matmul(X, w) + b
    y += torch.normal(0, 0.01, y.shape)
    return X, torch.reshape(y, (-1, 1))

def linreg(X, w, b):
    return torch.matmul(X, w) + b

def squared_loss(y_hat, y):
    return (y_hat - torch.reshape(y, y_hat.shape)) ** 2 / 2

def sgd(params, lr, batch_size):
    with torch.no_grad():
        for param in params:
            param -= lr * param.grad / batch_size
            param.grad.zero_()


def load_array(data_arrays, batch_size, is_train=True):
    dataset = data.TensorDataset(*data_arrays)
    return data.DataLoader(dataset, batch_size, shuffle=is_train)

def get_fashion_mnist_labels(labels):
    text_labels = ['t-shirt', 'trouser', 'pullover', 'dress', 'coat',
                   'sandal', 'shirt', 'sneaker', 'bag', 'ankle boot']
    return [text_labels[int(i)] for i in labels]

def show_images(imgs, num_rows, num_cols, titles=None, scale=1.5):
    figsize = (num_cols * scale, num_rows * scale)
    _, axes = plt.subplots(num_rows, num_cols, figsize=figsize)
    axes = axes.flatten()
    for i, (ax, img) in enumerate(zip(axes, imgs)):
        if torch.is_tensor(img):
            # Tensor Image
            ax.imshow(img.numpy())
        else:
            # PIL Image
            ax.imshow(img)
        ax.axes.get_xaxis().set_visible(False)
        ax.axes.get_yaxis().set_visible(False)
        if titles:
            ax.set_title(titles[i])
    return axes

def get_dataloader_workers():
    return 4


def load_data_fashion_mnist(batch_size, root, resize=None, download=True):
    trans = [transforms.ToTensor()]
    if resize:
        trans.insert(0, transforms.Resize(resize))#将图片短边缩放至resize，长宽比保持不变
    trans = transforms.Compose(trans)
    mnist_train = torchvision.datasets.FashionMNIST(root=root, train=True, transform=trans, download=download)
    mnist_test = torchvision.datasets.FashionMNIST(root=root, train=False, transform=trans, download=download,)
    return (data.DataLoader(mnist_train, batch_size, shuffle=True, num_workers=4), 
            data.DataLoader(mnist_test, batch_size, shuffle=True, num_workers=4))


def init_weights(net):
    if isinstance(net, torch.nn.Linear):
        torch.nn.init.normal_(net.weight, mean=0., std=0.01)
        # print(net.weight)
    #此处没写完，后续断更新

#如果net为sequential结构可以使用net.apply(init_weights) ，apply函数是nn.Module中实现的, 递归地调用self.children() 去处理自己以及子模块


# 返回预测正确的个数
def accuracy(y_hat, y):  #@save
    """计算预测正确的数量"""
    if len(y_hat.shape) > 1 and y_hat.shape[1] > 1:
        y_hat = y_hat.argmax(axis=1)
    cmp = y_hat.type(y.dtype) == y
    return float(cmp.type(y.dtype).sum())

# 给定模型net和数据集返回模型在这个数据集上的分类正确率
def evaluate_accuracy(net, data_iter):  #@save
    """计算在指定数据集上模型的精度"""
    if isinstance(net, torch.nn.Module):
        net.eval()  # 将模型设置为评估模式
    metric = Accumulator(2)  # 正确预测数、预测总数
    with torch.no_grad():
        for X, y in data_iter:
            metric.add(accuracy(net(X), y), y.numel())
    return metric[0] / metric[1]

# 返回模型net在某个数据集上的平均损失
def evaluate_loss(net, data_iter, loss):
    metric = Accumulator(2)  # Sum of losses, no. of examples
    for X, y in data_iter:
        out = net(X)
        y = torch.reshape(y, out.shape)
        l = loss(out, y)
        metric.add(l.sum(), y.numel())
    return metric[0] / metric[1]


class Accumulator:
    def __init__(self, n):
        self.data = [0.0] * n

    def add(self, *args):
        self.data = [a + float(b) for a, b in zip(self.data, args)]

    def reset(self):
        self.data = [0.0] * len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


# 定义一个在动画中绘制数据的实用程序类
class Animator:
    def __init__(self, xlabel=None, ylabel=None, legend=None, xlim=None, ylim=None, xscale='linear', yscale='linear',
                 fmts=('-', 'm--', 'g-.', 'r:'), nrows=1, ncols=1, figsize=(3.5, 2.5)):
        use_svg_display()
        #self.fig, self.axes = plt.subplots(nrows, ncols, figsize=figsize)
        self.fig, self.axes = plt.subplots(nrows, ncols)
        if nrows * ncols == 1:
            self.axes = [self.axes,]
        #定义了一个config_axes的函数，用于设置self.axes[0]
        self.config_axes = lambda:set_axes(self.axes[0], xlabel, ylabel, xlim, ylim, xscale, yscale, legend)

        self.X, self.Y, self.fmts = None, None, fmts
    # 向图表中添加多个数据点,x期望为一个数表示epoch，y期望为一个列表，里面的元素表示当前epoch的一些指标，一般为train loss, train acc, test acc
    def add(self, x, y):
        n = len(y)
        if isinstance(y, (int, float)):
            n = 1
        x = [x]*n
        #创建两个二维list
        if not self.X:
            self.X = [[] for _ in range(n)]
        if not self.Y:
            self.Y = [[] for _ in range(n)]
        #X与Y中的第i个列表分别对应着一条曲线的横坐标与纵坐标
        for i, (a, b) in enumerate(zip(x, y)):
            self.X[i].append(a)
            self.Y[i].append(b)
        self.axes[0].cla()
        for x, y, fmt in zip(self.X, self.Y, self.fmts):
            # print(x, y)
            self.axes[0].plot(x, y, fmt)
        self.config_axes()
        plt.pause(0.001)
        #在jupyter中用下面两句代码
        display.display(self.fig)
        display.clear_output(wait=True)



def visit_params_and_grads(net, epoch=None):
    with torch.no_grad():
        if epoch is None:
            for model in net.children():
                for param in model.parameters():
                    print('{}  Params VALUE  :\n{}'.format(model, param))
                    print('{}  Params GRAD   :\n{}'.format(model, param.grad.data))
        else:
            for model in net.children():
                for param in model.parameters():
                    print('epoch:{}   {}  Params VALUE  :\n{}'.format(epoch, model, param))
                    print('{}  Params GRAD   :\n{}'.format(model, param.grad.data))



def visit_params(net):
    with torch.no_grad():
        for model in net.children():
            for param in model.parameters():
                print('{}  Params VALUE  :\n{}'.format(model, param))


def train_epoch_for_regression(net, train_iter, loss, updater, 
                                epoch=None, check_params=False, monitor_grad=False, visit_param_changed=False):
    if isinstance(net, torch.nn.Module):
        net.train()
    metric = Accumulator(2)
    for X, y in train_iter:
        y_hat = net(X)

        l = loss(y_hat, y)
        if isinstance(updater, torch.optim.Optimizer):
            updater.zero_grad()

            if monitor_grad:
                # print('接下来将要展示loss对所有网络的输入和输出的梯度值:')
                print('---> next will show all networks inputs and outputs grads:')

            l.mean().backward()

            if visit_param_changed:
                # print('接下来将要展示更新之前的参数:')
                print('---> next will show parameters before update:')
                visit_params(net)
                # print('接下来将要展示更新后的参数值和此次更新时的参数的梯度大小:')
                print('---> next will show parameters after updating and show parameters grads:')

            updater.step()
            if check_params:
                if epoch is None:
                    visit_params_and_grads(net)
                else:
                    visit_params_and_grads(net, epoch)
        else:
            # Using custom built optimizer & loss criterion
            l.sum().backward()
            updater(X.shape[0])
        metric.add(float(l.sum()), y.numel())
    # Return training loss
    return metric[0] / metric[1]


def train_epoch_for_classify(net, train_iter, loss, updater, 
                epoch=None, check_params=False, monitor_grad=False, visit_param_changed=False):
    if isinstance(net, torch.nn.Module):
        net.train()
    metric = Accumulator(3)
    for X, y in train_iter:
        y_hat = net(X)

        l = loss(y_hat, y)
        if isinstance(updater, torch.optim.Optimizer):
            updater.zero_grad()

            if monitor_grad:
                # print('接下来将要展示loss对所有网络的输入和输出的梯度值:')
                print('---> next will show all networks inputs and outputs grads:')

            l.mean().backward()

            if visit_param_changed:
                # print('接下来将要展示更新之前的参数:')
                print('---> next will show parameters before update:')
                visit_params(net)
                print('---> next will show parameters after updating and show parameters grads:')
                # print('接下来将要展示更新后的参数值和此次更新时的参数的梯度大小:')

            updater.step()
            if check_params:
                if epoch is None:
                    visit_params_and_grads(net)
                else:
                    visit_params_and_grads(net, epoch)
        else:
            # Using custom built optimizer & loss criterion
            l.sum().backward()
            updater(X.shape[0])
        metric.add(float(l.sum()), accuracy(y_hat, y), y.numel())
    # Return training loss and training accuracy
    return metric[0] / metric[2], metric[1] / metric[2]


def monitor_grad_hook(module, grad_input, grad_output):
    if grad_output[0] is not None:
        # print('loss 对  {}   OUTPUT 的 Grad_Shape:{}  GRAD:\n{}'.format(module, grad_output[0].shape, grad_output[0]))
        print('loss dui  {}   OUTPUT  Grad_Shape:{}  GRAD:\n{}'.format(module, grad_output[0].shape, grad_output[0]))
    if grad_input[0] is not None:
        print('loss dui  {}   INPUT   Grad_Shape:{}  GRAD:\n{}'.format(module, grad_input[0].shape, grad_input[0]))


def train_classify(net, train_iter, test_iter, loss, num_epochs, updater, 
        check_params=False, monitor_grad=False, visit_param_changed=False):
    handles = []
    if isinstance(net, nn.Module):
        if monitor_grad:
            for model in net.children():
                handles.append(model.register_full_backward_hook(monitor_grad_hook))

    animator = Animator(xlabel='epoch', xlim=[1, num_epochs], ylim=[0, 1],
                        legend=['train loss', 'train acc', 'test acc'])

    if test_iter is None:
        for epoch in range(num_epochs):

            print(' '*30, 'Current Epoch:{}'.format(epoch))

            train_metrics = train_epoch_for_classify(net, train_iter, loss, updater, epoch, check_params, monitor_grad, visit_param_changed)

            print(' '*30, 'Current Epoch:{}'.format(epoch))
            print('Train loss:{}, Train acc:{}'.format(train_metrics[0], train_metrics[1]))

            animator.add(epoch + 1, train_metrics)
    else:
        for epoch in range(num_epochs):

            print(' '*30, 'Current Epoch:{}'.format(epoch))

            train_metrics = train_epoch_for_classify(net, train_iter, loss, updater, epoch, check_params, monitor_grad, visit_param_changed)
            test_acc = evaluate_accuracy(net, test_iter)

            print(' '*30,'Current Epoch:{}'.format(epoch))
            print('Train loss:{}, Train acc:{}, Test acc:{}'.format(train_metrics[0], train_metrics[1], test_acc))

            animator.add(epoch + 1, train_metrics + (test_acc,))

    if(len(handles) > 0):
        for handle in handles:
            handle.remove()
    
    plt.show()


def train_regression(net, train_iter, test_iter, loss, num_epochs, updater, 
        check_params=False, monitor_grad=False, visit_param_changed=False):
    handles = []
    if isinstance(net, nn.Module):
        if monitor_grad:
            for model in net.children():
                handles.append(model.register_full_backward_hook(monitor_grad_hook))


    animator = Animator(xlabel='epoch', xlim=[1, num_epochs], ylim=None,
                        legend=['train loss', 'test loss'])

    if test_iter is None:
        for epoch in range(num_epochs):

            print(' '*30, 'Current Epoch:{}'.format(epoch))

            train_metrics = train_epoch_for_regression(net, train_iter, loss, updater, epoch, check_params, monitor_grad, visit_param_changed)

            print(' '*30, 'Current Epoch:{}'.format(epoch))
            print('Train loss:{}'.format(train_metrics))

            animator.add(epoch + 1, train_metrics)
    else:
        for epoch in range(num_epochs):

            print(' '*30, 'Current Epoch:{}'.format(epoch))

            train_metrics = train_epoch_for_regression(net, train_iter, loss, updater, epoch, check_params, monitor_grad, visit_param_changed)
            test_loss = evaluate_loss(net, test_iter, loss)

            print(' '*30,'Current Epoch:{}'.format(epoch))
            print('Train loss:{}, Test loss:{}'.format(train_metrics, test_loss))

            animator.add(epoch + 1, [train_metrics,test_loss])

    if(len(handles) > 0):
        for handle in handles:
            handle.remove()
    
    plt.show()




def predict(net, test_iter, n = 6):
    for x, y in test_iter:
        y_hat = net(x).argmax(axis=1)
        truelabels = get_fashion_mnist_labels(y)
        prelabels = get_fashion_mnist_labels(y_hat)
        titles = ['true:'+true+'\n' + 'pre:'+pred for true, pred in zip(truelabels, prelabels)]
        show_images(x[0:n].reshape(n, 28, 28), num_rows=1, num_cols=n, titles=titles)