# -*- coding: utf-8 -*-
"""
Created on Thu Jul 10 14:04:13 2025
@author: zzha962
"""
import torch
import torch.nn as nn
from typing import Dict

# ========== MoE Classifier ==========
class MoEClassifier(nn.Module):
    def __init__(self, backbone_dims: Dict[str, int], hidden_dim=128, gate_temp=1.0):
        super().__init__()
        self.backbones = list(backbone_dims.keys())
        self.backbone_dims_list = [backbone_dims[b] for b in self.backbones]
        self.num_experts = len(self.backbones)
        self.total_dim = sum(self.backbone_dims_list)
        self.gate_temp = gate_temp

        self.experts = nn.ModuleDict({
            b: nn.Sequential(
                nn.Linear(backbone_dims[b], hidden_dim),
                nn.ReLU(inplace=True),
                nn.Linear(hidden_dim, 1)
            )
            for b in self.backbones
        })

        self.gate = nn.Sequential(
            nn.Linear(self.total_dim, hidden_dim),
            nn.ReLU(inplace=True),
            nn.Linear(hidden_dim, self.num_experts)
        )

    def forward(self, x):
        splits = torch.split(x, self.backbone_dims_list, dim=1)
        expert_logits = [self.experts[b](f) for b, f in zip(self.backbones, splits)]  # list [B,1]
        expert_logits = torch.cat(expert_logits, dim=1)  # [B,E]
        gate_raw = self.gate(x) / max(self.gate_temp, 1e-6)
        gate_w = torch.softmax(gate_raw, dim=1)  # [B,E]
        final_logits = torch.sum(expert_logits * gate_w, dim=1)  # [B]
        return final_logits, expert_logits, gate_w






