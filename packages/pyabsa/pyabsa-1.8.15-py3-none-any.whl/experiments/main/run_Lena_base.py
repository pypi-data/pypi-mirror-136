# -*- coding: utf-8 -*-
# file: run_Lena_large.py
# time: 2021/5/26 0026
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.

########################################################################################################################
#                    train and evaluate on your own apc_datasets (need train and test apc_datasets)                    #
########################################################################################################################
import random

from pyabsa.functional import Trainer
from pyabsa.functional import APCConfigManager
from pyabsa.functional import ABSADatasetList
from pyabsa.functional import APCModelList
import warnings

warnings.filterwarnings('ignore')
seeds = [random.randint(0, 10000) for _ in range(2)]

apc_config_english = APCConfigManager.get_apc_config_english()
apc_config_english.model = APCModelList.LSA_S
apc_config_english.lcf = 'cdw'
apc_config_english.similarity_threshold = 1
apc_config_english.max_seq_len = 80
apc_config_english.dropout = 0
apc_config_english.cache_dataset = True
apc_config_english.log_step = 10
apc_config_english.patience = 10
apc_config_english.pretrained_bert = 'microsoft/deberta-v3-base'
apc_config_english.hidden_dim = 768
apc_config_english.embed_dim = 768
apc_config_english.num_epoch = 25
apc_config_english.learning_rate = 1e-5
apc_config_english.batch_size = 16
apc_config_english.evaluate_begin = 5
apc_config_english.l2reg = 1e-7
apc_config_english.seed = seeds
apc_config_english.cross_validate_fold = -1  # disable cross_validate

Laptop14 = ABSADatasetList.Laptop14
Trainer(config=apc_config_english,
        dataset=Laptop14,  # train set and test set will be automatically detected
        checkpoint_save_mode=0,  # =None to avoid save model
        auto_device=True  # automatic choose CUDA or CPU
        )

Restaurant14 = ABSADatasetList.Restaurant14
Trainer(config=apc_config_english,
        dataset=Restaurant14,  # train set and test set will be automatically detected
        checkpoint_save_mode=0,  # =None to avoid save model
        auto_device=True  # automatic choose CUDA or CPU
        )

Restaurant15 = ABSADatasetList.Restaurant15
Trainer(config=apc_config_english,
        dataset=Restaurant15,  # train set and test set will be automatically detected
        checkpoint_save_mode=0,  # =None to avoid save model
        auto_device=True  # automatic choose CUDA or CPU
        )

Restaurant16 = ABSADatasetList.Restaurant16
Trainer(config=apc_config_english,
        dataset=Restaurant16,  # train set and test set will be automatically detected
        checkpoint_save_mode=0,  # =None to avoid save model
        auto_device=True  # automatic choose CUDA or CPU
        )

MAMS = ABSADatasetList.MAMS
Trainer(config=apc_config_english,
        dataset=MAMS,  # train set and test set will be automatically detected
        checkpoint_save_mode=0,  # =None to avoid save model
        auto_device=True  # automatic choose CUDA or CPU
        )

apc_config_english = APCConfigManager.get_apc_config_english()
apc_config_english.model = APCModelList.LSA_T
apc_config_english.lcf = 'cdw'
apc_config_english.similarity_threshold = 1
apc_config_english.max_seq_len = 80
apc_config_english.dropout = 0
apc_config_english.cache_dataset = True
apc_config_english.log_step = 10
apc_config_english.patience = 10
apc_config_english.pretrained_bert = 'microsoft/deberta-v3-base'
apc_config_english.hidden_dim = 768
apc_config_english.embed_dim = 768
apc_config_english.num_epoch = 25
apc_config_english.learning_rate = 1e-5
apc_config_english.batch_size = 16
apc_config_english.evaluate_begin = 5
apc_config_english.l2reg = 1e-7
apc_config_english.seed = seeds
apc_config_english.cross_validate_fold = -1  # disable cross_validate

Laptop14 = ABSADatasetList.Laptop14
Trainer(config=apc_config_english,
        dataset=Laptop14,  # train set and test set will be automatically detected
        checkpoint_save_mode=0,  # =None to avoid save model
        auto_device=True  # automatic choose CUDA or CPU
        )

Restaurant14 = ABSADatasetList.Restaurant14
Trainer(config=apc_config_english,
        dataset=Restaurant14,  # train set and test set will be automatically detected
        checkpoint_save_mode=0,  # =None to avoid save model
        auto_device=True  # automatic choose CUDA or CPU
        )

Restaurant15 = ABSADatasetList.Restaurant15
Trainer(config=apc_config_english,
        dataset=Restaurant15,  # train set and test set will be automatically detected
        checkpoint_save_mode=0,  # =None to avoid save model
        auto_device=True  # automatic choose CUDA or CPU
        )

Restaurant16 = ABSADatasetList.Restaurant16
Trainer(config=apc_config_english,
        dataset=Restaurant16,  # train set and test set will be automatically detected
        checkpoint_save_mode=0,  # =None to avoid save model
        auto_device=True  # automatic choose CUDA or CPU
        )

MAMS = ABSADatasetList.MAMS
Trainer(config=apc_config_english,
        dataset=MAMS,  # train set and test set will be automatically detected
        checkpoint_save_mode=0,  # =None to avoid save model
        auto_device=True  # automatic choose CUDA or CPU
        )
