import os
import torch
import numpy as np
from torch.utils.data import DataLoader, Dataset
import torch.nn as nn
import torch.optim as optim
from monai.networks.nets import VoxelMorphUNet, VoxelMorph
import matplotlib.pyplot as plt
from sklearn.model_selection import KFold
import nibabel as nib
import tensorflow as tf
import glob
from typing import Tuple, List
import torch.nn.functional as F
from datetime import datetime
import SimpleITK as sitk
from scipy.ndimage import rotate, shift, zoom, gaussian_filter

# Data augmentation functions for 3D medical images
def random_rotate(image, max_angle=10):
    """Apply random rotation to a 3D image"""
    angle_x = np.random.uniform(-max_angle, max_angle)
    angle_y = np.random.uniform(-max_angle, max_angle)
    angle_z = np.random.uniform(-max_angle, max_angle)
    
    rotated = rotate(image, angle_x, axes=(1, 2), reshape=False, order=1, mode='constant')
    rotated = rotate(rotated, angle_y, axes=(0, 2), reshape=False, order=1, mode='constant')
    rotated = rotate(rotated, angle_z, axes=(0, 1), reshape=False, order=1, mode='constant')
    
    return rotated

def random_shift(image, max_shift=5):
    """Apply random shift to a 3D image"""
    shift_x = np.random.uniform(-max_shift, max_shift)
    shift_y = np.random.uniform(-max_shift, max_shift)
    shift_z = np.random.uniform(-max_shift, max_shift)
    
    return shift(image, [shift_x, shift_y, shift_z], order=1, mode='constant')

def random_zoom(image, zoom_range=(0.9, 1.1)):
    """Apply random zoom to a 3D image"""
    zoom_factor = np.random.uniform(zoom_range[0], zoom_range[1])
    
    # Keep aspect ratio
    zoom_matrix = [zoom_factor, zoom_factor, zoom_factor]
    
    zoomed = zoom(image, zoom_matrix, order=1, mode='constant')
    
    # Crop or pad to original size
    result = np.zeros_like(image)
    
    # Get new and old shapes
    new_shape = zoomed.shape
    old_shape = image.shape
    
    # Calculate slices for cropping or padding
    slices_new = [slice(0, min(new_shape[i], old_shape[i])) for i in range(3)]
    slices_old = [slice(0, min(new_shape[i], old_shape[i])) for i in range(3)]
    
    # Copy data
    result[slices_old[0], slices_old[1], slices_old[2]] = zoomed[slices_new[0], slices_new[1], slices_new[2]]
    
    return result

def random_flip(image):
    """Apply random flip to a 3D image"""
    # Create a copy to avoid negative strides
    result = image.copy()
    
    # Apply flips with copy
    flip_x = np.random.choice([True, False])
    flip_y = np.random.choice([True, False])
    flip_z = np.random.choice([True, False])
    
    if flip_x:
        result = np.flip(result, axis=0).copy()
    if flip_y:
        result = np.flip(result, axis=1).copy()
    if flip_z:
        result = np.flip(result, axis=2).copy()
    
    return result



def augment_image(image, augment_prob=0.5):
    """Apply a series of random augmentations with probability"""
    if np.random.rand() < augment_prob:
        image = random_rotate(image)
    if np.random.rand() < augment_prob:
        image = random_shift(image)
    if np.random.rand() < augment_prob:
        image = random_zoom(image)
    if np.random.rand() < augment_prob:
        image = random_flip(image)
    return image

# Crop function using SimpleITK
def crop_fraction(image, fractions):
    """
    Crop an image based on fractional sizes.
    
    Args:
        image: The SimpleITK image object.
        fractions: Tuple of fractions (e.g., (4/8, 4/8, 8/8)).
        
    Returns:
        Cropped SimpleITK image.
    """
    original_size = np.array(image.GetSize())
    start_fraction = (1 - np.array(fractions)) / 2  # Calculate start as fraction
    end_fraction = start_fraction + np.array(fractions)  # Calculate end as fraction
    
    # Determine start and end indices
    start_index = np.floor(original_size * start_fraction).astype(int)
    end_index = np.floor(original_size * end_fraction).astype(int)
    crop_size = end_index - start_index
    
    # Define cropping
    crop_filter = sitk.RegionOfInterestImageFilter()
    crop_filter.SetIndex(start_index.tolist())
    crop_filter.SetSize(crop_size.tolist())
    cropped_image = crop_filter.Execute(image)
    
    return cropped_image

# Load and crop a NIfTI file
def load_and_crop_nifti(file_path: str, fractions=(4/8, 4/8, 8/8)) -> np.ndarray:
    """Load a NIfTI file, crop it, and return its data array."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    # Read with SimpleITK
    sitk_image = sitk.ReadImage(file_path)
    
    # Crop the image
    cropped_image = crop_fraction(sitk_image, fractions)
    
    # Convert to numpy array
    data = sitk.GetArrayFromImage(cropped_image)
    
    # SimpleITK uses (z, y, x) ordering, convert to (x, y, z)
    data = np.transpose(data, (2, 1, 0))
    
    return data

# Normalize image using percentile clipping
def normalize_image(img: np.ndarray) -> np.ndarray:
    """Normalize image using percentile clipping."""
    if img.size == 0:
        raise ValueError("Empty image array")
    p1, p99 = np.percentile(img, (1, 99))
    if p1 == p99:
        return np.zeros_like(img)
    img = np.clip(img, p1, p99)
    return (img - p1) / (p99 - p1)

# Resize a 3D volume using TensorFlow's resize operation
def resize_volume(img: np.ndarray, target_shape: Tuple[int, int, int]) -> np.ndarray:
    """Resize a 3D volume using TensorFlow's resize operation."""
    if len(img.shape) != 3:
        raise ValueError(f"Expected 3D input, got shape {img.shape}")
    
    img_tensor = tf.convert_to_tensor(img, dtype=tf.float32)
    img_tensor = tf.expand_dims(img_tensor, axis=0)

    # Perform 3D resize
    resized = tf.transpose(img_tensor, [0, 3, 1, 2])
    resized = tf.image.resize(resized,
                            size=(target_shape[2], target_shape[0]),
                            method='bilinear')
    resized = tf.transpose(resized, [0, 2, 3, 1])
    resized = tf.image.resize(resized,
                            size=(target_shape[0], target_shape[1]),
                            method='bilinear')

    return tf.squeeze(resized, axis=0).numpy()

# Prepare and process medical imaging data with cropping
def prepare_data(adc_dir: str, t2_dir: str,
                target_shape: Tuple[int, int, int] = (128, 128, 32),
                crop_fractions: Tuple[float, float, float] = (4/8, 4/8, 8/8)) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    """Prepare and process medical imaging data with cropping."""
    if not os.path.exists(adc_dir):
        raise ValueError(f"ADC directory not found: {adc_dir}")
    if not os.path.exists(t2_dir):
        raise ValueError(f"T2 directory not found: {t2_dir}")

    adc_files = sorted(glob.glob(os.path.join(adc_dir, '*.nii.gz')))
    adc_files.extend(sorted(glob.glob(os.path.join(adc_dir, '*.nii'))))
    
    t2_files = sorted(glob.glob(os.path.join(t2_dir, '*.nii.gz')))
    t2_files.extend(sorted(glob.glob(os.path.join(t2_dir, '*.nii'))))

    print(f"Found {len(adc_files)} ADC and {len(t2_files)} T2 files")

    adc_data = []
    t2_data = []
    file_names = []

    for adc_file, t2_file in zip(adc_files, t2_files):
        try:
            # Check file size first to avoid "Empty file" errors
            if os.path.getsize(adc_file) == 0 or os.path.getsize(t2_file) == 0:
                print(f"Skipping empty file(s): {adc_file} or {t2_file}")
                continue
                
            # Load and crop images
            adc_img = load_and_crop_nifti(adc_file, crop_fractions)
            t2_img = load_and_crop_nifti(t2_file, crop_fractions)

            # Resize to target shape if needed
            if adc_img.shape != target_shape:
                adc_img = resize_volume(adc_img, target_shape)
            if t2_img.shape != target_shape:
                t2_img = resize_volume(t2_img, target_shape)

            # Normalize images
            adc_img = normalize_image(adc_img)
            t2_img = normalize_image(t2_img)

            adc_data.append(adc_img)
            t2_data.append(t2_img)
            file_names.append(os.path.basename(adc_file))

            print(f"Processed {os.path.basename(adc_file)}")
            print(f"Shapes - ADC: {adc_img.shape}, T2: {t2_img.shape}")

        except Exception as e:
            print(f"Error processing {adc_file}: {str(e)}")
            continue

    if not adc_data:
        raise ValueError("No valid images were processed")

    adc_data = np.expand_dims(np.stack(adc_data), axis=-1)
    t2_data = np.expand_dims(np.stack(t2_data), axis=-1)

    print(f"\nFinal dataset shapes:")
    print(f"ADC data: {adc_data.shape}")
    print(f"T2 data: {t2_data.shape}")

    return adc_data, t2_data, file_names

# Dataset class for medical images with augmentation
# AugmentedMedicalImageDataset with fixed negative stride issue
class AugmentedMedicalImageDataset(Dataset):
    def __init__(self, moving_data, fixed_data, filenames=None, augment=False, augment_prob=0.5):
        self.moving_data = moving_data
        self.fixed_data = fixed_data
        self.filenames = filenames if filenames is not None else [f"sample_{i}" for i in range(len(moving_data))]
        self.augment = augment
        self.augment_prob = augment_prob

    def __len__(self):
        return len(self.moving_data)

    def __getitem__(self, idx):
        moving = self.moving_data[idx].squeeze().copy()  # Create a copy to avoid negative stride issues
        fixed = self.fixed_data[idx].squeeze().copy()    # Create a copy to avoid negative stride issues
        
        # Apply augmentation only during training if enabled
        if self.augment:
            # Generate the same random seed for both images to ensure consistent augmentation
            seed = np.random.randint(2147483647)
            np.random.seed(seed)
            moving = augment_image(moving, self.augment_prob)
            np.random.seed(seed)
            fixed = augment_image(fixed, self.augment_prob)
        
        # Add channel dimension back and convert to tensor
        moving = np.expand_dims(moving, axis=0)
        fixed = np.expand_dims(fixed, axis=0)
        
        # Ensure contiguous arrays before tensor conversion to avoid stride issues
        moving = np.ascontiguousarray(moving)
        fixed = np.ascontiguousarray(fixed)
        
        moving = torch.tensor(moving, dtype=torch.float32)
        fixed = torch.tensor(fixed, dtype=torch.float32)
        
        return moving, fixed, self.filenames[idx]

# Loss function for VoxelMorph
class VoxelMorphLoss(nn.Module):
    def __init__(self, alpha=0.05, beta=0.25):
        super().__init__()
        self.alpha = alpha
        self.beta = beta
        self.reconstruction_loss = nn.MSELoss()
        self.similarity_loss = nn.L1Loss()
        self.ncc_loss = NormalizedCrossCorrelationLoss()

    def forward(self, warped, fixed, ddf):
        # MSE and L1 loss for structural similarity
        mse_loss = self.reconstruction_loss(warped, fixed)
        l1_loss = self.similarity_loss(warped, fixed)

        # NCC loss for multi-modal alignment
        ncc_loss = self.ncc_loss(warped, fixed)

        # Gradient loss for smoother deformation
        gradient_loss = self.calculate_gradient_loss(ddf)

        return mse_loss + self.beta * (l1_loss + ncc_loss) + self.alpha * gradient_loss

    def calculate_gradient_loss(self, ddf):
        dx = torch.abs(ddf[:, :, 1:, :, :] - ddf[:, :, :-1, :, :])
        dy = torch.abs(ddf[:, :, :, 1:, :] - ddf[:, :, :, :-1, :])
        dz = torch.abs(ddf[:, :, :, :, 1:] - ddf[:, :, :, :, :-1])

        d2x = torch.abs(ddf[:, :, 2:, :, :] + ddf[:, :, :-2, :, :] - 2*ddf[:, :, 1:-1, :, :])
        d2y = torch.abs(ddf[:, :, :, 2:, :] + ddf[:, :, :, :-2, :] - 2*ddf[:, :, :, 1:-1, :])
        d2z = torch.abs(ddf[:, :, :, :, 2:] + ddf[:, :, :, :, :-2] - 2*ddf[:, :, :, :, 1:-1])

        return (torch.mean(dx) + torch.mean(dy) + torch.mean(dz) +
                0.5 * (torch.mean(d2x) + torch.mean(d2y) + torch.mean(d2z)))

# Normalized Cross Correlation Loss
class NormalizedCrossCorrelationLoss(nn.Module):
    def __init__(self, window_size=7):
        super().__init__()
        self.window_size = window_size

    def forward(self, x, y):
        """
        Compute local NCC loss between two images.
        """
        # Compute local means
        kernel_size = [self.window_size] * 3
        padding = [self.window_size // 2] * 3

        # Compute local statistics
        x_mean = F.avg_pool3d(x, kernel_size, stride=1, padding=padding)
        y_mean = F.avg_pool3d(y, kernel_size, stride=1, padding=padding)

        x_var = F.avg_pool3d(x * x, kernel_size, stride=1, padding=padding) - x_mean * x_mean
        y_var = F.avg_pool3d(y * y, kernel_size, stride=1, padding=padding) - y_mean * y_mean
        xy_cov = F.avg_pool3d(x * y, kernel_size, stride=1, padding=padding) - x_mean * y_mean

        # Add small constant to avoid division by zero
        epsilon = 1e-5
        ncc = xy_cov / torch.sqrt(x_var * y_var + epsilon)

        return -torch.mean(ncc)

# Initialize model - using the original model architecture
def create_model():
    backbone = VoxelMorphUNet(
        spatial_dims=3,
        in_channels=2,
        unet_out_channels=32,
        channels=(16, 32, 32, 32),
        final_conv_channels=(16,)
    )

    model = VoxelMorph(
        backbone=backbone,
        integration_steps=10,
        half_res=True
    )
    
    return model

# Train the model for a single fold with data augmentation
def train_fold(fold_idx, train_idx, val_idx, adc_data, t2_data, filenames, num_epochs, device, output_dir, augment=True):
    print(f"\n{'='*20} Training Fold {fold_idx + 1} with {'augmentation' if augment else 'no augmentation'} {'='*20}")
    
    # Create folder for this fold
    fold_dir = os.path.join(output_dir, f"fold_{fold_idx+1}")
    os.makedirs(fold_dir, exist_ok=True)
    
    # Split data for this fold
    adc_train = adc_data[train_idx]
    adc_val = adc_data[val_idx]
    t2_train = t2_data[train_idx]
    t2_val = t2_data[val_idx]
    
    # Get filenames for this fold
    train_filenames = [filenames[i] for i in train_idx]
    val_filenames = [filenames[i] for i in val_idx]
    
    # Create datasets and dataloaders with augmentation for training
    train_dataset = AugmentedMedicalImageDataset(adc_train, t2_train, train_filenames, augment=augment, augment_prob=0.5)
    val_dataset = AugmentedMedicalImageDataset(adc_val, t2_val, val_filenames, augment=False)  # No augmentation for validation

    # Reduce batch size to prevent OOM errors
    train_loader = DataLoader(train_dataset, batch_size=1, shuffle=True, num_workers=2)
    val_loader = DataLoader(val_dataset, batch_size=1, shuffle=False, num_workers=2)

    # Initialize model
    model = create_model()
    model = model.to(device)

    # Initialize optimizer
    optimizer = optim.AdamW(
        model.parameters(),
        lr=1e-4,
        weight_decay=0.01
    )

    # Initialize loss function
    loss_function = VoxelMorphLoss(alpha=0.05, beta=0.25)

    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, verbose=True
    )

    # Training
    best_val_loss = float('inf')
    patience = 15
    patience_counter = 0
    train_losses = []
    val_losses = []

    for epoch in range(num_epochs):
        # Training phase
        model.train()
        epoch_train_loss = 0
        for moving, fixed, _ in train_loader:
            moving, fixed = moving.to(device), fixed.to(device)

            optimizer.zero_grad()
            warped, ddf = model(moving, fixed)
            loss = loss_function(warped, fixed, ddf)

            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

            epoch_train_loss += loss.item()

        avg_train_loss = epoch_train_loss / len(train_loader)
        train_losses.append(avg_train_loss)

        # Validation phase
        model.eval()
        epoch_val_loss = 0
        with torch.no_grad():
            for moving, fixed, _ in val_loader:
                moving, fixed = moving.to(device), fixed.to(device)
                warped, ddf = model(moving, fixed)
                loss = loss_function(warped, fixed, ddf)
                epoch_val_loss += loss.item()

        avg_val_loss = epoch_val_loss / len(val_loader)
        val_losses.append(avg_val_loss)

        # Learning rate scheduling
        scheduler.step(avg_val_loss)

        print(f'Epoch {epoch+1}/{num_epochs}:')
        print(f'Training Loss: {avg_train_loss:.4f}')
        print(f'Validation Loss: {avg_val_loss:.4f}')

        # Save checkpoint every 10 epochs
        if (epoch + 1) % 10 == 0:
            checkpoint_path = os.path.join(fold_dir, f'checkpoint_epoch_{epoch+1}.pth')
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': avg_train_loss,
                'val_loss': avg_val_loss,
            }, checkpoint_path)

        # Save best model
        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
            best_model_path = os.path.join(fold_dir, 'best_model.pth')
            torch.save(model.state_dict(), best_model_path)
            print(f"Saved new best model with val_loss: {best_val_loss:.4f}")
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f'Early stopping triggered after {epoch+1} epochs')
                break

    # Plot training history
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Training Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.title(f'VoxelMorph Training History - Fold {fold_idx+1} - {"With" if augment else "Without"} Augmentation')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(fold_dir, 'training_history.png'))
    plt.close()

    return {
        'fold': fold_idx + 1,
        'best_val_loss': best_val_loss,
        'train_losses': train_losses,
        'val_losses': val_losses
    }

# Train with cross-validation and data augmentation
def train_with_cross_validation(adc_data, t2_data, filenames, n_folds=5, num_epochs=50, device="cuda", augment=True):
    # Create output directory with augmentation info
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"voxelmorph_cv_{timestamp}_{'aug' if augment else 'noaug'}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save info about augmentation
    with open(os.path.join(output_dir, 'training_info.txt'), 'w') as f:
        f.write(f"Training with data augmentation: {augment}\n")
        f.write(f"Number of folds: {n_folds}\n")
        f.write(f"Number of epochs: {num_epochs}\n")
        f.write(f"Dataset size: {len(filenames)} samples\n")
        if augment:
            f.write("\nAugmentation techniques used:\n")
            f.write(" - Random rotation (±10 degrees)\n")
            f.write(" - Random shift (±5 voxels)\n")
            f.write(" - Random zoom (0.9-1.1x)\n")
            f.write(" - Random flips (x, y, z axes)\n")
    
    # Create KFold object
    kfold = KFold(n_splits=n_folds, shuffle=True, random_state=42)
    
    # Store results for each fold
    fold_results = []
    
    # Train each fold
    for fold_idx, (train_idx, val_idx) in enumerate(kfold.split(adc_data)):
        fold_result = train_fold(
            fold_idx=fold_idx,
            train_idx=train_idx,
            val_idx=val_idx,
            adc_data=adc_data,
            t2_data=t2_data,
            filenames=filenames,
            num_epochs=num_epochs,
            device=device,
            output_dir=output_dir,
            augment=augment  # Pass augmentation flag
        )
        fold_results.append(fold_result)
    
    # Find the best fold
    best_fold_idx = np.argmin([result['best_val_loss'] for result in fold_results])
    best_fold = fold_results[best_fold_idx]['fold']
    best_val_loss = fold_results[best_fold_idx]['best_val_loss']
    
    print(f"\n{'='*20} Cross-Validation Results {'='*20}")
    for result in fold_results:
        print(f"Fold {result['fold']}: Best Val Loss = {result['best_val_loss']:.4f}")
    
    print(f"\nBest fold: {best_fold} with validation loss: {best_val_loss:.4f}")
    
    # Copy the best model to the output directory
    best_model_path = os.path.join(output_dir, f"fold_{best_fold}", 'best_model.pth')
    final_best_model_path = os.path.join(output_dir, 'best_model.pth')
    
    import shutil
    shutil.copy2(best_model_path, final_best_model_path)
    
    print(f"Best model copied to: {final_best_model_path}")
    
    # Plot comparison of all folds
    plt.figure(figsize=(12, 8))
    for result in fold_results:
        plt.plot(result['val_losses'], label=f"Fold {result['fold']}")
    
    plt.title(f'Validation Loss Across Folds - {"With" if augment else "Without"} Augmentation')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'cross_validation_comparison.png'))
    plt.close()
    
    return best_fold, best_val_loss, output_dir

# Train final model using all data with data augmentation
def train_final_model(adc_data, t2_data, filenames, num_epochs=50, device="cuda", best_model_path=None, augment=True):
    print(f"\n{'='*20} Training Final Model on All Data with {'augmentation' if augment else 'no augmentation'} {'='*20}")
    
    # Create output directory with augmentation info
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = f"voxelmorph_final_{timestamp}_{'aug' if augment else 'noaug'}"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create dataset and dataloader with augmentation
    dataset = AugmentedMedicalImageDataset(adc_data, t2_data, filenames, augment=augment, augment_prob=0.5)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=True, num_workers=2)
    
    # Initialize model
    model = create_model()
    
    # Load best model weights if provided
    if best_model_path and os.path.exists(best_model_path):
        print(f"Loading weights from best model: {best_model_path}")
        model.load_state_dict(torch.load(best_model_path, map_location=device))
    
    model = model.to(device)
    
    # Initialize optimizer
    optimizer = optim.AdamW(
        model.parameters(),
        lr=1e-4,
        weight_decay=0.01
    )
    
    # Initialize loss function
    loss_function = VoxelMorphLoss(alpha=0.05, beta=0.25)
    
    # Training
    best_loss = float('inf')
    train_losses = []
    best_model_state = None
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        epoch_loss = 0
        
        for moving, fixed, _ in dataloader:
            moving, fixed = moving.to(device), fixed.to(device)
            
            optimizer.zero_grad()
            warped, ddf = model(moving, fixed)
            loss = loss_function(warped, fixed, ddf)
            
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            epoch_loss += loss.item()
        
        avg_epoch_loss = epoch_loss / len(dataloader)
        train_losses.append(avg_epoch_loss)
        
        print(f'Epoch {epoch+1}/{num_epochs}:')
        print(f'Training Loss: {avg_epoch_loss:.4f}')
        
        # Save checkpoint every 10 epochs
        if (epoch + 1) % 10 == 0:
            checkpoint_path = os.path.join(output_dir, f'checkpoint_epoch_{epoch+1}.pth')
            torch.save({
                'epoch': epoch + 1,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'train_loss': avg_epoch_loss,
            }, checkpoint_path)
        
        # Save best model
        if avg_epoch_loss < best_loss:
            best_loss = avg_epoch_loss
            best_model_state = model.state_dict().copy()
            best_model_path = os.path.join(output_dir, 'best_model.pth')
            torch.save(best_model_state, best_model_path)
            print(f"Saved new best model with loss: {best_loss:.4f}")
    
    # Make sure the model has the best weights
    if best_model_state is not None:
        model.load_state_dict(best_model_state)
        print(f"Loaded best model weights (loss: {best_loss:.4f}) for final model")
    
    # Plot training history
    plt.figure(figsize=(10, 6))
    plt.plot(train_losses, label='Training Loss')
    plt.title(f'Final Model Training History - {"With" if augment else "Without"} Augmentation')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'training_history.png'))
    plt.close()
    
    print(f"Best model saved to: {best_model_path}")
    return model, best_loss, output_dir

def main():
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Set PyTorch memory allocation configuration for better memory management
    if device.type == 'cuda':
        torch.cuda.empty_cache()
        # Try to enable more efficient memory allocation
        os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    
    try:
        # Get all cluster folders
        base_dir = 'clusters'  # Base directory containing all clusters
        cluster_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith('cluster')]
        print(f"Found {len(cluster_dirs)} clusters: {cluster_dirs}")
        
        # Initialize lists to hold all data
        all_adc_data = []
        all_t2_data = []
        all_filenames = []
        
        # Process each cluster
        for cluster in cluster_dirs:
            adc_dir = os.path.join(base_dir, cluster, 'warped_adc')
            t2_dir = os.path.join(base_dir, cluster, 't2')
            
            if not os.path.exists(adc_dir) or not os.path.exists(t2_dir):
                print(f"Skipping {cluster} due to missing directories")
                continue
                
            print(f"\nProcessing {cluster}...")
            
            # Process the data for this cluster
            try:
                # Use smaller target shape to reduce memory requirements
                cluster_adc_data, cluster_t2_data, cluster_filenames = prepare_data(
                    adc_dir=adc_dir,
                    t2_dir=t2_dir,
                    target_shape=(64, 64, 32),  # Reduced from 96x96 to 64x64
                    crop_fractions=(4/8, 4/8, 8/8)
                )
                
                # Append to the combined dataset
                all_adc_data.append(cluster_adc_data)
                all_t2_data.append(cluster_t2_data)
                # Add cluster prefix to filenames to avoid duplicates
                all_filenames.extend([f"{cluster}_{filename}" for filename in cluster_filenames])
                
                print(f"Added {len(cluster_filenames)} patients from {cluster}")
                
            except Exception as e:
                print(f"Error processing {cluster}: {str(e)}")
                continue
        
        # Combine all data
        if not all_adc_data:
            raise ValueError("No valid data was found in any cluster")
            
        combined_adc_data = np.concatenate(all_adc_data, axis=0)
        combined_t2_data = np.concatenate(all_t2_data, axis=0)
        
        print(f"\nCombined dataset shape:")
        print(f"ADC data: {combined_adc_data.shape}")
        print(f"T2 data: {combined_t2_data.shape}")
        print(f"Total patients: {len(all_filenames)}")
        
        # Optional: If still having memory issues, sample a subset of the data
        # Adjust max_samples based on your GPU memory capacity
        max_samples = 186  # Adjust this number based on your GPU memory
        if len(all_filenames) > max_samples:
            print(f"\nReducing dataset size from {len(all_filenames)} to {max_samples} due to memory constraints")
            indices = np.random.choice(len(all_filenames), max_samples, replace=False)
            combined_adc_data = combined_adc_data[indices]
            combined_t2_data = combined_t2_data[indices]
            all_filenames = [all_filenames[i] for i in indices]
        
        # Step 2: Cross-validation training with data augmentation
        print("\nStep 2: Starting cross-validation training with data augmentation...")
        best_fold, best_val_loss, cv_output_dir = train_with_cross_validation(
            adc_data=combined_adc_data,
            t2_data=combined_t2_data,
            filenames=all_filenames,
            n_folds=5,
            num_epochs=100,  # Reduced number of epochs
            device=device,
            augment=True  # Enable data augmentation
        )
        
        # Clear memory before final training
        if device.type == 'cuda':
            torch.cuda.empty_cache()
        
        # Step 3: Train final model on all data with data augmentation
        print("\nStep 3: Training final model on all data with data augmentation...")
        best_model_path = os.path.join(cv_output_dir, 'best_model.pth')
        final_model, final_loss, final_output_dir = train_final_model(
            adc_data=combined_adc_data,
            t2_data=combined_t2_data,
            filenames=all_filenames,
            num_epochs=100,  # Reduced number of epochs
            device=device,
            best_model_path=best_model_path,
            augment=True  # Enable data augmentation
        )
        
        print(f"\nTraining completed successfully!")
        print(f"Best cross-validation fold: {best_fold}")
        print(f"Best validation loss: {best_val_loss:.4f}")
        print(f"Final model best training loss: {final_loss:.4f}")
        print(f"Best model saved at: {os.path.join(final_output_dir, 'best_model.pth')}")
        
        # Clear memory before visualization
        if device.type == 'cuda':
            torch.cuda.empty_cache()

        
        # Optional: Generate visualization of augmentation examples
        print("\nGenerating visualization of augmentation examples...")
        aug_output_dir = os.path.join(final_output_dir, 'augmentation_examples')
        os.makedirs(aug_output_dir, exist_ok=True)
        
        # Choose a few samples for visualization
        sample_indices = np.random.choice(len(combined_adc_data), min(3, len(combined_adc_data)), replace=False)
        
        for i, idx in enumerate(sample_indices):
            # Original image
            original_moving = combined_adc_data[idx].squeeze()
            original_fixed = combined_t2_data[idx].squeeze()
            
            # Apply augmentation
            seed = np.random.randint(2147483647)
            np.random.seed(seed)
            aug_moving = augment_image(original_moving.copy(), augment_prob=1.0)  # Force all augmentations
            np.random.seed(seed)
            aug_fixed = augment_image(original_fixed.copy(), augment_prob=1.0)  # Force all augmentations
            
            # Visualize
            mid_slice = original_moving.shape[2] // 2
            
            plt.figure(figsize=(12, 6))
            
            plt.subplot(2, 2, 1)
            plt.imshow(original_moving[:, :, mid_slice], cmap='gray')
            plt.title('Original ADC')
            plt.axis('off')
            
            plt.subplot(2, 2, 2)
            plt.imshow(original_fixed[:, :, mid_slice], cmap='gray')
            plt.title('Original T2')
            plt.axis('off')
            
            plt.subplot(2, 2, 3)
            plt.imshow(aug_moving[:, :, mid_slice], cmap='gray')
            plt.title('Augmented ADC')
            plt.axis('off')
            
            plt.subplot(2, 2, 4)
            plt.imshow(aug_fixed[:, :, mid_slice], cmap='gray')
            plt.title('Augmented T2')
            plt.axis('off')
            
            plt.suptitle(f'Sample {i+1} - Augmentation Comparison')
            plt.tight_layout()
            plt.savefig(os.path.join(aug_output_dir, f'sample_{i+1}_augmentation.png'))
            plt.close()
        
        print(f"Augmentation examples saved to: {aug_output_dir}")
        
        # Visualize individual augmentation effects
        print("\nGenerating visualization of individual augmentation effects...")
        aug_effects_dir = os.path.join(final_output_dir, 'augmentation_effects')
        os.makedirs(aug_effects_dir, exist_ok=True)
        
        # Use first sample for demonstration
        sample_idx = sample_indices[0]
        sample_img = combined_adc_data[sample_idx].squeeze().copy()
        
        # Apply each augmentation individually
        augmentations = [
            ('Original', sample_img),
            ('Random Rotation', random_rotate(sample_img.copy())),
            ('Random Shift', random_shift(sample_img.copy())),
            ('Random Zoom', random_zoom(sample_img.copy())),
            ('Random Flip', random_flip(sample_img.copy()))
        ]
        
        # Create grid visualization
        plt.figure(figsize=(15, 12))
        for i, (title, img) in enumerate(augmentations):
            plt.subplot(3, 3, i+1)
            plt.imshow(img[:, :, img.shape[2]//2], cmap='gray')
            plt.title(title)
            plt.axis('off')
        
        plt.suptitle('Individual Augmentation Effects')
        plt.tight_layout()
        plt.savefig(os.path.join(aug_effects_dir, 'augmentation_effects.png'))
        plt.close()
        
        print(f"Augmentation effects visualization saved to: {aug_effects_dir}")
        
    except Exception as e:
        print(f"Error during execution: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()