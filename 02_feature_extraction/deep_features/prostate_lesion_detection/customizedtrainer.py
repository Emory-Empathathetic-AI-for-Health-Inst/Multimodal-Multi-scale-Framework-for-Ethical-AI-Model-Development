import os


trainer_path = "/content/nnUNet/nnunetv2/training/nnUNetTrainer/nnUNetTrainer_FinalSOTAKillVersion.py"


trainer_code = '''
import os
import warnings


os.environ["DYNAMIC_NETWORK_ARCHITECTURES_DISABLE_FFT"] = "1"

warnings.filterwarnings("ignore", message="Using a non-tuple sequence")
warnings.filterwarnings("ignore", message=".*GradScaler.*deprecated.*")

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from torch.cuda.amp import autocast, GradScaler

from nnunetv2.training.nnUNetTrainer.nnUNetTrainer import nnUNetTrainer
from nnunetv2.preprocessing.gland_crop_utils import box_mask_crop


# 🔹 ROBUST CE

class RobustCrossEntropy(nn.Module):
    def __init__(self, weight=None, reduction="mean"):
        super().__init__()
        self.weight = weight
        self.reduction = reduction

    def forward(self, inputs, targets):
        log_probs = F.log_softmax(inputs, dim=1)
        return F.nll_loss(log_probs, targets, weight=self.weight, reduction=self.reduction)



#  FOCAL + RCE combined loss

class CombinedLoss(nn.Module):
    def __init__(self, alpha=0.9, gamma=1.5, rce_weight=0.3, focal_weight=0.5):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.rce_weight = rce_weight
        self.focal_weight = focal_weight
        self.rce_loss = RobustCrossEntropy(
            weight=torch.tensor([0.01, 0.99], device="cuda")
        )

    def forward(self, inputs, targets):
        targets = targets.squeeze(1).long()

        ce = F.cross_entropy(inputs, targets, reduction="none")
        pt = torch.exp(-ce)

        focal_weight = torch.clamp((1 - pt) ** self.gamma, min=0.05)
        focal_loss = (self.alpha * focal_weight * ce).mean()

        rce_loss = self.rce_loss(inputs, targets)
        return self.focal_weight * focal_loss + self.rce_weight * rce_loss


# ======================================================
# 🚀 FINAL TRAINER
# ======================================================
class nnUNetTrainer_FinalSOTAKillVersion(nnUNetTrainer):
    def __init__(self, plans, configuration, fold, dataset_json, device):
        print("🔥 Final Trainer (FAST + gland-crop + ciPCa negatives)")
        super().__init__(plans, configuration, fold, dataset_json, device)

      
        self.enable_compile = False

        self.initial_lr = 5e-4
        self.batch_size = 2
        self.num_epochs = 100

        self.configuration_manager._default_num_epochs = 100
        self.configuration_manager.max_num_epochs = 100

        self.scaler = GradScaler()

    def _should_compile(self):
        return False

    def build_loss(self):
        return CombinedLoss()

    def on_train_start(self):
   
        # GLAND-BASED CROP
      
        self.configuration_manager.crop_function = box_mask_crop

  
        # ciPCa NEGATIVE SAMPLING
    
        self.label_minimum_fraction_of_foreground = 0.0
        self.label_minimum_fraction_of_foreground_class = 0.0
        self.enable_fg_balance_for_foreground_classes = True

       
        self.do_dummy_2d_data_aug = False
        self.configuration_manager.do_dummy_2d_data_aug = False

        self.configuration_manager._patch_size = np.array([24, 192, 192])
        self.configuration_manager._patch_size_for_spatialtransform = np.array([24, 192, 192])

        self._patch_size = np.array([24, 192, 192])
        self._patch_size_for_spatialtransform = np.array([24, 192, 192])
        self._batch_size = 2

        
        # STANDARD AUG
        
        self.enable_mirroring = True
        self.rotation_for_DA = (-20, 20)
        self.scale_range = (0.8, 1.3)

        print(f"⏱️ Training capped at {self.num_epochs} epochs.")
        super().on_train_start()

    def initialize_optimizer_and_scheduler(self):
        self.optimizer = torch.optim.AdamW(
            self.network.parameters(),
            lr=self.initial_lr,
            weight_decay=1e-5
        )

        self.lr_scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            self.optimizer,
            T_0=10,
            T_mult=2,
            eta_min=1e-4
        )

    def training_step(self, batch):
        data = batch["data"]
        target = batch["target"]

        self.optimizer.zero_grad(set_to_none=True)

        with autocast():
            output = self.network(data)
            loss = self.loss(output, target)

        self.scaler.scale(loss).backward()
        self.scaler.step(self.optimizer)
        self.scaler.update()

        return loss.detach().cpu().numpy()
'''

#write trainer
with open(trainer_path, "w") as f:
    f.write(trainer_code)

print("Trainer UPDATED ")





#train command
!nnUNetv2_train 001 3d_fullres 0 -tr nnUNetTrainer_FinalSOTAKillVersion

#can train all folds together as well 
