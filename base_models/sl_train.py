#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 14 21:57:57 2021

@author: guansanghai

singularity shell --nv --bind $HOME /share/koikoi_organizers/koikoi_3.8.17.sif
"""

import argparse
import os
import pickle
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import numpy as np
import torch  # 1.8.1
import torch.utils.data as data

from base_models.koikoinet2L import DiscardModel, KoiKoiModel, PickModel
from base_models.yaku_distance import get_yaku

torch.set_printoptions(edgeitems=1000)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
model_save_dir = "outputs/model_sl"

if not os.path.exists(model_save_dir):
    os.makedirs(model_save_dir)


def get_filename_list(dataset_path, record_num_list):
    filename_list = []
    for root, dirs, files in os.walk(dataset_path):
        for file in files:
            if file.endswith(".pickle") and int(file.split("_")[0]) in record_num_list:
                filename_list.append(file)
    return filename_list


class KoiKoiSLDataset(data.Dataset):
    def __init__(self, dataset_path, record_num_list):
        self.data = []
        filename_list = get_filename_list(dataset_path, record_num_list)
        self.filename_list = filename_list
        for ii, filename in enumerate(filename_list):
            with open(dataset_path + filename, "rb") as f:
                sample = pickle.load(f)
            self.data.append(sample)
            if (ii + 1) % 1000 == 0:
                print(f"{ii+1} samples loaded...")
        print(f"All {ii+1} samples loaded over!")

    def __getitem__(self, index):
        sample = self.data[index]
        # print(self.filename_list[index])
        return sample["feature"], sample["result"]

    def __len__(self):
        return len(self.data)


class KoiKoiSLTrainer:
    def __init__(self, task_name, w_yaku_loss: float):
        self.task_name = task_name
        self.w_yaku_loss = w_yaku_loss

        # koikoigame/koikoigame.py class KoiKoiCard
        # tensorでのインデックスを表す
        cards = {
            "crane": {
                0,
            },
            "curtain": {
                8,
            },
            "moon": {
                28,
            },
            "rainman": {
                40,
            },
            "phenix": {
                44,
            },
            "sake": {
                32,
            },
            "light": {0, 8, 28, 40, 44},
            "seed": {4, 12, 16, 20, 24, 29, 32, 36, 41},
            "ribon": {1, 5, 9, 13, 17, 21, 25, 33, 37, 42},
        }
        cards["dross"] = (
            set(list(i for i in range(48)))
            - cards["light"]
            - cards["seed"]
            - cards["ribon"]
        )
        self.cards = cards

        self.yaku_tensor = torch.zeros((48, 12))  # 各役に必要なカードの0-1表現
        # five lights, four lights, rainy four lights, three lights
        # boar-dear-butterfly, flower viewing sake, moon viewing sake, tane
        # red ribbon, blue ribbon, tan
        # kasu

        yaku_win_count = torch.tensor(
            [2, 4, 46, 169, 76, 249, 249, 237, 73, 63, 418, 520]
        )
        self.yaku_win_rate = yaku_win_count / torch.sum(yaku_win_count)
        self.yaku_win_rate = self.yaku_win_rate.to(device).reshape((-1, 1))

        for i in self.cards["light"]:
            self.yaku_tensor[i][0] = 1
            self.yaku_tensor[i][1] = 1
            self.yaku_tensor[i][2] = 1
            self.yaku_tensor[i][3] = 1
        # 猪鹿蝶
        for i in {
            20,
            24,
            36,
        }:
            self.yaku_tensor[i][4] = 1
        # 花見酒
        self.yaku_tensor[8][5] = 1
        self.yaku_tensor[32][5] = 1
        # 月見酒
        self.yaku_tensor[28][6] = 1
        self.yaku_tensor[32][6] = 1
        # タネ
        for i in self.cards["seed"]:
            self.yaku_tensor[i][7] = 1
        # 赤丹
        self.yaku_tensor[1][8] = 1
        self.yaku_tensor[5][8] = 1
        self.yaku_tensor[9][8] = 1
        # 青丹
        self.yaku_tensor[21][9] = 1
        self.yaku_tensor[33][9] = 1
        self.yaku_tensor[37][9] = 1
        # 丹
        for i in self.cards["ribon"]:
            self.yaku_tensor[i][10] = 1
        # カス
        for i in self.cards["dross"]:
            self.yaku_tensor[i][11] = 1
        # 役方向に正規化
        self.yaku_tensor = self.yaku_tensor / torch.sum(
            self.yaku_tensor, dim=1, keepdim=True
        )
        self.yaku_tensor = self.yaku_tensor.to(device)

    def init_dataset(self, dataset_path, k_fold, test_fold, batch_size, record_num=200):
        self.k_fold = k_fold
        self.test_fold = test_fold
        print("Loading train dataset...")
        train_record_index = [
            ii for ii in range(1, record_num + 1) if ii % k_fold != test_fold
        ]
        train_dataset = KoiKoiSLDataset(dataset_path, train_record_index)
        self.train_loader = data.DataLoader(
            dataset=train_dataset, batch_size=batch_size, shuffle=True, drop_last=True
        )
        print("Loading test dataset...")
        test_record_index = [
            ii for ii in range(1, record_num + 1) if ii % k_fold == test_fold
        ]
        test_dataset = KoiKoiSLDataset(dataset_path, test_record_index)
        self.test_loader = data.DataLoader(dataset=test_dataset, batch_size=batch_size)
        return

    def init_model(self, net_model, transfer_model_path=None, lr=1e-3):
        self.model = net_model().to(device)
        if transfer_model_path is not None:
            trained_model = torch.load(transfer_model_path)
            model_state_dict = self.model.state_dict()
            update_state_dict = {
                k: v
                for k, v in trained_model.state_dict().items()
                if k in model_state_dict.keys()
            }
            model_state_dict.update(update_state_dict)
            self.model.load_state_dict(model_state_dict)
            print(f"Trained model {transfer_model_path} loaded!")
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)
        self.criterion = torch.nn.CrossEntropyLoss().to(device)
        return

    def train(self, epoch_num):
        best_acc = 0
        for epoch in range(epoch_num):
            acc, loss = self.__forward_prop(self.train_loader, update_model=True)
            print(f"\nEpoch {epoch+1} train over, acc = {acc:.3f}, loss = {loss:.5f}")

            acc, loss = self.__forward_prop(self.test_loader, update_model=False)
            print(f"Epoch {epoch+1} test over, acc = {acc:.3f}, loss = {loss:.5f}")

            if acc > best_acc:
                best_acc = acc
                path = f"{model_save_dir}/{self.task_name}_fold_{self.k_fold}_{self.test_fold}.pt"
                torch.save(self.model, path)
                print(f"Model {path} saved!")
        return

    def __forward_prop(self, data_loader, update_model=True):
        def accuracy(output, result):
            return np.sum(output == result) / float(len(output))

        if update_model:
            self.model.train()
        else:
            self.model.eval()

        acc_list, loss_list = [], []
        for step, (feature, result) in enumerate(data_loader):
            # feature = (batch, 300, 48)
            output = self.model(feature.to(device))
            output = output.to(device)
            if self.w_yaku_loss != 0:
                yaku_loss = self.yaku_loss(feature_tensor=feature, model_output=output)
            else:
                yaku_loss = 0
            loss = (
                self.criterion(output, result.to(device)) + yaku_loss * self.w_yaku_loss
            )

            if update_model:
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()

            output = output.argmax(dim=1).cpu().detach().numpy()
            result = result.cpu().detach().numpy()
            acc_list.append(accuracy(output, result))
            loss_list.append(loss.item())

        return np.mean(acc_list), np.mean(loss_list)

    def yaku_loss(self, feature_tensor, model_output) -> torch.Tensor:
        """calculate yaku loss

        Args:
            feature_tensor (torch.Tensor): feature tensor. shape=(batch, 300, 48)
            model_output (torch.Tensor): model output tensor. shape=(batch, 48)

        Returns:
            torch.Tensor:  yaku loss. shape=(batch)
        """
        # feature_tensor = feature_tensor.to(device)
        # assert len(feature_tensor) == len(model_output)  # check same batch size
        # previous_hand = feature_tensor[:, 166, :]
        # next_hand_prob = previous_hand + model_output

        yaku_loss = model_output @ self.yaku_tensor @ self.yaku_win_rate
        return torch.mean(yaku_loss)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--w_yaku_loss", type=float, default=0.0)
    parser.add_argument(
        "--task_name",
        help="discard, pick, or koikoi",
        type=str,
        choices=["discard", "pick", "koikoi"],
    )
    parser.add_argument("--epochs", type=int, default=20)
    parser.add_argument("--batch", type=int, default=512)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    task_name = args.task_name
    if task_name != "pick":
        args.w_yaku_loss = 0.0
    dataset_path = f"../KoiKoi-AI/dataset/{task_name}/"  # FIXME: hard coded
    # このrepoと同じ階層にKoiKoi-AIの元論文repoを置いてあるものとする
    # そのため，このrepoは別名でcloneされている必要あり
    net_model = {"discard": DiscardModel, "pick": PickModel, "koikoi": KoiKoiModel}[
        task_name
    ]
    trained_model_path = None

    trainer = KoiKoiSLTrainer(task_name, w_yaku_loss=args.w_yaku_loss)
    trainer.init_dataset(dataset_path, k_fold=5, test_fold=0, batch_size=args.batch)
    trainer.init_model(net_model, trained_model_path, lr=0.0001)
    trainer.train(epoch_num=args.epochs)
