import os
import torch
import numpy as np
from torch.utils.data import DataLoader, Dataset
from monai.networks.nets import VoxelMorphUNet, VoxelMorph
import nibabel as nib
import tensorflow as tf
import glob
import SimpleITK as sitk
from typing import Tuple, List
from pathlib import Path
import matplotlib.pyplot as plt

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
def load_and_crop_nifti(file_path: str, fractions=(4/8, 4/8, 8/8)) -> Tuple[np.ndarray, np.ndarray]:
    """Load a NIfTI file, crop it, and return its data array and affine."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Load original image to get affine
        nib_img = nib.load(file_path)
        affine = nib_img.affine
        
        # Read with SimpleITK for cropping
        sitk_image = sitk.ReadImage(file_path)
        
        # Crop the image
        cropped_image = crop_fraction(sitk_image, fractions)
        
        # Convert to numpy array
        data = sitk.GetArrayFromImage(cropped_image)
        
        # SimpleITK uses (z, y, x) ordering, convert to (x, y, z)
        data = np.transpose(data, (2, 1, 0))
        
        return data, affine
    except Exception as e:
        print(f"Error loading/cropping {file_path}: {str(e)}")
        return None, None

# Load a NIfTI file and return its data array
def load_nifti(file_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Load a NIfTI file and return its data array and affine."""
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        nii = nib.load(file_path)
        return nii.get_fdata(), nii.affine
    except Exception as e:
        print(f"Error loading {file_path}: {str(e)}")
        return None, None

# Normalize image using percentile clipping
def normalize_image(img: np.ndarray) -> np.ndarray:
    """Normalize image using percentile clipping."""
    if img is None or img.size == 0:
        return None
    try:
        p1, p99 = np.percentile(img, (1, 99))
        if p1 == p99:
            return np.zeros_like(img)
        img = np.clip(img, p1, p99)
        return (img - p1) / (p99 - p1)
    except Exception as e:
        print(f"Error normalizing image: {str(e)}")
        return None

# Resize a 3D volume using TensorFlow's resize operation
def resize_volume(img: np.ndarray, target_shape: Tuple[int, int, int]) -> np.ndarray:
    """Resize a 3D volume using TensorFlow's resize operation."""
    if img is None:
        return None
    try:
        if len(img.shape) != 3:
            raise ValueError(f"Expected 3D input, got shape {img.shape}")
        
        # Check if resize is needed
        if img.shape == target_shape:
            return img
            
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
    except Exception as e:
        print(f"Error resizing volume: {str(e)}")
        return None

# Dataset class for medical images
class MedicalImageDataset(Dataset):
    def __init__(self, moving_data, fixed_data, filenames=None, affines=None):
        self.moving_data = moving_data
        self.fixed_data = fixed_data
        self.filenames = filenames if filenames is not None else [f"sample_{i}" for i in range(len(moving_data))]
        self.affines = affines if affines is not None else [np.eye(4) for _ in range(len(moving_data))]

    def __len__(self):
        return len(self.moving_data)

    def __getitem__(self, idx):
        moving = torch.tensor(self.moving_data[idx], dtype=torch.float32).permute(3, 0, 1, 2)
        fixed = torch.tensor(self.fixed_data[idx], dtype=torch.float32).permute(3, 0, 1, 2)
        return moving, fixed, self.filenames[idx], self.affines[idx]

# Initialize VoxelMorph model
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

# Prepare data for a single cluster with cropping
def prepare_cluster_data(adc_dir: str, t2_dir: str, 
                        target_shape: Tuple[int, int, int] = (96, 96, 32),
                        crop_fractions: Tuple[float, float, float] = (4/8, 4/8, 8/8)) -> Tuple[np.ndarray, np.ndarray, List[str], List[np.ndarray]]:
    """Prepare data for a single cluster with cropping."""
    print(f"Processing data from directories: {adc_dir} and {t2_dir}")
    
    if not os.path.exists(adc_dir):
        print(f"ADC directory not found: {adc_dir}")
        return np.array([]), np.array([]), [], []
        
    if not os.path.exists(t2_dir):
        print(f"T2 directory not found: {t2_dir}")
        return np.array([]), np.array([]), [], []

    # Look for both .nii.gz and .nii files
    adc_files = sorted(glob.glob(os.path.join(adc_dir, '*.nii.gz')))
    adc_files.extend(sorted(glob.glob(os.path.join(adc_dir, '*.nii'))))
    
    t2_files = sorted(glob.glob(os.path.join(t2_dir, '*.nii.gz')))
    t2_files.extend(sorted(glob.glob(os.path.join(t2_dir, '*.nii'))))

    print(f"Found {len(adc_files)} ADC and {len(t2_files)} T2 files")

    adc_data = []
    t2_data = []
    file_names = []
    affines = []
    valid_pairs = 0

    # Match ADC and T2 files by name
    for adc_file in adc_files:
        adc_base = os.path.basename(adc_file).replace('_adc', '').replace('.nii.gz', '').replace('.nii', '')
        
        # Find matching T2 file
        t2_file = None
        for t2_path in t2_files:
            t2_base = os.path.basename(t2_path).replace('_t2', '').replace('_t2w', '').replace('.nii.gz', '').replace('.nii', '')
            if adc_base == t2_base:
                t2_file = t2_path
                break
        
        if t2_file is None:
            print(f"No matching T2 file found for {adc_file}")
            continue
        
        try:
            # Load images with cropping and get affine matrix
            adc_img, adc_affine = load_and_crop_nifti(adc_file, crop_fractions)
            t2_img, _ = load_and_crop_nifti(t2_file, crop_fractions)
            
            if adc_img is None or t2_img is None or adc_affine is None:
                continue

            # Resize to target shape if needed
            if adc_img.shape != target_shape:
                adc_img = resize_volume(adc_img, target_shape)
            if t2_img.shape != target_shape:
                t2_img = resize_volume(t2_img, target_shape)
            
            if adc_img is None or t2_img is None:
                continue

            # Normalize images
            adc_img = normalize_image(adc_img)
            t2_img = normalize_image(t2_img)
            
            if adc_img is None or t2_img is None:
                continue

            adc_data.append(adc_img)
            t2_data.append(t2_img)
            file_names.append(os.path.basename(adc_file))
            affines.append(adc_affine)
            valid_pairs += 1

            print(f"Processed pair: {os.path.basename(adc_file)} and {os.path.basename(t2_file)}")

        except Exception as e:
            print(f"Error processing {adc_file}: {str(e)}")
            continue

    if not adc_data:
        print("No valid image pairs were processed in this cluster")
        return np.array([]), np.array([]), [], []

    adc_data = np.expand_dims(np.stack(adc_data), axis=-1)
    t2_data = np.expand_dims(np.stack(t2_data), axis=-1)

    print(f"\nProcessed {valid_pairs} valid image pairs")
    print(f"Final dataset shapes for this cluster:")
    print(f"ADC data: {adc_data.shape}")
    print(f"T2 data: {t2_data.shape}")

    return adc_data, t2_data, file_names, affines

# Apply model to dataset and save results
def apply_model_to_dataset(model, adc_data, t2_data, filenames, affines, device, output_dir, dataset_name):
    """Apply model to dataset and save registered images."""
    if len(adc_data) == 0 or len(t2_data) == 0:
        print(f"No data to process for dataset {dataset_name}")
        return
    
    # Create dataset and dataloader
    dataset = MedicalImageDataset(adc_data, t2_data, filenames, affines)
    dataloader = DataLoader(dataset, batch_size=1, shuffle=False, num_workers=2)
    
    # Create output directory
    results_dir = os.path.join(output_dir, dataset_name)
    os.makedirs(results_dir, exist_ok=True)
    
    # Set model to evaluation mode
    model.eval()
    
    with torch.no_grad():
        for moving, fixed, filename, affine in dataloader:
            # Move tensors to the selected device
            moving, fixed = moving.to(device), fixed.to(device)
            
            # Apply registration
            warped, ddf = model(moving, fixed)
            
            # Convert tensors to numpy arrays
            moving_np = moving.cpu().numpy().squeeze()
            fixed_np = fixed.cpu().numpy().squeeze()
            warped_np = warped.cpu().numpy().squeeze()
            ddf_np = ddf.cpu().numpy().squeeze()
            affine_np = affine.numpy().squeeze()
            
            # Save registered image as NIfTI
            warped_nii = nib.Nifti1Image(warped_np, affine_np)
            warped_filename = os.path.join(results_dir, f"{filename[0]}_warped.nii.gz")
            nib.save(warped_nii, warped_filename)
            
            # Save original images for reference
            moving_nii = nib.Nifti1Image(moving_np, affine_np)
            fixed_nii = nib.Nifti1Image(fixed_np, affine_np)
            moving_filename = os.path.join(results_dir, f"{filename[0]}_moving.nii.gz")
            fixed_filename = os.path.join(results_dir, f"{filename[0]}_fixed.nii.gz")
            nib.save(moving_nii, moving_filename)
            nib.save(fixed_nii, fixed_filename)
            
            # Save deformation field
            ddf_nii = nib.Nifti1Image(np.transpose(ddf_np, (1, 2, 3, 0)), affine_np)
            ddf_filename = os.path.join(results_dir, f"{filename[0]}_ddf.nii.gz")
            nib.save(ddf_nii, ddf_filename)
            
            # Also create a visualization image for quick inspection
            visualize_registration(moving_np, fixed_np, warped_np, results_dir, filename[0])
            
            print(f"Saved registration results for {filename[0]}")

# Create visualization of registration results
def visualize_registration(moving, fixed, warped, output_dir, filename):
    """Create and save visualization of registration results."""
    # Get middle slices for visualization
    z_middle = moving.shape[2] // 2
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # Plot moving image (ADC)
    axes[0, 0].imshow(moving[:, :, z_middle], cmap='gray')
    axes[0, 0].set_title('Moving Image (ADC)')
    axes[0, 0].axis('off')
    
    # Plot fixed image (T2W)
    axes[0, 1].imshow(fixed[:, :, z_middle], cmap='gray')
    axes[0, 1].set_title('Fixed Image (T2W)')
    axes[0, 1].axis('off')
    
    # Plot registered image
    axes[1, 0].imshow(warped[:, :, z_middle], cmap='gray')
    axes[1, 0].set_title('Registered Image')
    axes[1, 0].axis('off')
    
    # Plot difference image
    diff = fixed[:, :, z_middle] - warped[:, :, z_middle]
    axes[1, 1].imshow(diff, cmap='bwr', vmin=-0.5, vmax=0.5)
    axes[1, 1].set_title('Difference (Fixed - Registered)')
    axes[1, 1].axis('off')
    
    # Save figure
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{filename}_registration.png"))
    plt.close()

def main():
    # Set device
    device = torch.device("cuda:1" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    # Set paths - UPDATE THESE PATHS
    model_path = "/home/sazamat/data/PIQUALvsMRQy_study/voxelmorph_final_20250415_202821_aug/best_model.pth"  # Use best_model.pth instead of final_model.pth
    base_dir = "/home/sazamat/data/PIQUALvsMRQy_study/clusters"
    output_dir = os.path.join(base_dir, "registration_results")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize model
    model = create_model()
    
    # Load model weights
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        print(f"Loaded model from {model_path}")
    else:
        print(f"Error: Model file not found at {model_path}")
        return
    
    model = model.to(device)
    
    # Process each cluster
    for cluster_id in range(1, 7):  # Clusters 1-6
        print(f"\n{'='*50}")
        print(f"Processing Cluster {cluster_id}")
        print(f"{'='*50}")
        
        # Set paths for this cluster
        adc_dir = os.path.join(base_dir, f"cluster{cluster_id}", "warped_adc")
        t2_dir = os.path.join(base_dir, f"cluster{cluster_id}", "t2")
        
        # Prepare data with cropping
        adc_data, t2_data, filenames, affines = prepare_cluster_data(
            adc_dir=adc_dir,
            t2_dir=t2_dir,
            target_shape=(96, 96, 32),
            crop_fractions=(4/8, 4/8, 8/8)  # Apply the same cropping as during training
        )
        
        # Apply model and save results
        if len(adc_data) > 0:
            dataset_name = f"cluster{cluster_id}"
            apply_model_to_dataset(
                model=model,
                adc_data=adc_data,
                t2_data=t2_data,
                filenames=filenames,
                affines=affines,
                device=device,
                output_dir=output_dir,
                dataset_name=dataset_name
            )
            print(f"Completed processing for Cluster {cluster_id}")
        else:
            print(f"No valid data found for Cluster {cluster_id}, skipping...")
    
    print("\nAll clusters processed. Registration results saved to:")
    print(output_dir)

if __name__ == "__main__":
    main()