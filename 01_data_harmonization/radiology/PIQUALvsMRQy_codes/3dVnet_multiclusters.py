import os
import glob
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import nibabel as nib
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
import matplotlib.pyplot as plt

# Base path for all clusters
base_path = "/PIQUALvsMRQy_study/PIQUALvsMRQy_server/PIQUALvsMRQy_study_server_segmentation_experiment/PIQUALvsMRQy_segmentations"

# List of cluster directories
cluster_dirs = [
    "cluster1_t2",
    "cluster2_t2",
    "cluster3_t2",
    "cluster4_t2",
    "cluster5_t2",
    "cluster6_t2"
]

# Number of cases to select from each cluster
cases_per_cluster = 10

# Function to get a subset of cases from each cluster
def get_cluster_subset(cluster_path, num_cases=10):
    # Get all image files from the cluster
    image_files = sorted(glob.glob(os.path.join(cluster_path, "*_t2w.nii.gz")))
    segmentation_files = sorted(glob.glob(os.path.join(cluster_path, "*_gland.nii.gz")))
    
    print(f"Found {len(image_files)} images and {len(segmentation_files)} segmentations in {cluster_path}")
    
    # Ensure we have paired image and segmentation files
    paired_files = []
    for img_file in image_files:
        base_name = os.path.basename(img_file).replace("_t2w.nii.gz", "")
        seg_file = os.path.join(os.path.dirname(img_file), f"{base_name}_gland.nii.gz")
        if seg_file in segmentation_files:
            paired_files.append((img_file, seg_file))
    
    # Randomly select num_cases if we have more than needed
    if len(paired_files) > num_cases:
        selected_pairs = random.sample(paired_files, num_cases)
    else:
        selected_pairs = paired_files
    
    selected_images = [pair[0] for pair in selected_pairs]
    selected_segmentations = [pair[1] for pair in selected_pairs]
    
    print(f"Selected {len(selected_images)} cases from {cluster_path}")
    
    return selected_images, selected_segmentations

# Gather subset from each cluster
all_image_files = []
all_segmentation_files = []

for cluster in cluster_dirs:
    cluster_path = os.path.join(base_path, cluster)
    if os.path.exists(cluster_path):
        img_files, seg_files = get_cluster_subset(cluster_path, cases_per_cluster)
        all_image_files.extend(img_files)
        all_segmentation_files.extend(seg_files)
    else:
        print(f"Warning: Cluster path {cluster_path} not found, skipping")

print(f"Total cases selected: {len(all_image_files)}")

# Data loading and preprocessing function
def load_and_preprocess_data(image_files, segmentation_files):
    images = []
    segmentations = []
    
    for img_file, seg_file in zip(image_files, segmentation_files):
        # Load image and segmentation
        img_nib = nib.load(img_file)
        seg_nib = nib.load(seg_file)
        
        # Get data
        img_data = img_nib.get_fdata()
        seg_data = seg_nib.get_fdata()
        
        # Normalize image data to [0, 1]
        img_data = (img_data - img_data.min()) / (img_data.max() - img_data.min())
        
        # Convert segmentation to binary
        seg_data = (seg_data > 0).astype(np.float32)
        
        # Add channel dimension
        img_data = np.expand_dims(img_data, axis=-1)
        seg_data = np.expand_dims(seg_data, axis=-1)
        
        images.append(img_data)
        segmentations.append(seg_data)
    
    return np.array(images), np.array(segmentations)

# Load and preprocess data
X, y = load_and_preprocess_data(all_image_files, all_segmentation_files)

print(f"Data loaded with shape: {X.shape}, {y.shape}")

# Create data generator with augmentation
def data_generator(X, y, batch_size=2):
    while True:
        # Get random indexes
        indexes = np.random.randint(0, len(X), batch_size)
        
        batch_X = X[indexes]
        batch_y = y[indexes]
        
        # Simple augmentations
        for i in range(batch_size):
            # Random flip
            if np.random.random() > 0.5:
                batch_X[i] = np.flip(batch_X[i], axis=0)
                batch_y[i] = np.flip(batch_y[i], axis=0)
            
            if np.random.random() > 0.5:
                batch_X[i] = np.flip(batch_X[i], axis=1)
                batch_y[i] = np.flip(batch_y[i], axis=1)
            
            if np.random.random() > 0.5:
                batch_X[i] = np.flip(batch_X[i], axis=2)
                batch_y[i] = np.flip(batch_y[i], axis=2)
        
        yield batch_X, batch_y

# Define custom Dice loss and coefficient
def dice_loss(y_true, y_pred, smooth=1.0):
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    return 1 - (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)

def dice_coefficient(y_true, y_pred, smooth=1.0):
    y_true_f = tf.reshape(y_true, [-1])
    y_pred_f = tf.reshape(y_pred, [-1])
    intersection = tf.reduce_sum(y_true_f * y_pred_f)
    return (2. * intersection + smooth) / (tf.reduce_sum(y_true_f) + tf.reduce_sum(y_pred_f) + smooth)

# Define V-Net architecture
def build_vnet(input_shape, n_filters=16):
    inputs = layers.Input(input_shape)
    
    # Stage 1 - Encoder
    conv1 = layers.Conv3D(n_filters, kernel_size=3, padding='same')(inputs)
    conv1 = layers.PReLU()(conv1)
    conv1 = layers.Conv3D(n_filters, kernel_size=3, padding='same')(conv1)
    conv1 = layers.PReLU()(conv1)
    # Residual connection
    res1 = layers.Conv3D(n_filters, kernel_size=1, padding='same')(inputs)
    conv1 = layers.Add()([conv1, res1])
    # Downsampling with strided convolution
    pool1 = layers.Conv3D(n_filters*2, kernel_size=2, strides=2, padding='same')(conv1)
    pool1 = layers.PReLU()(pool1)
    
    # Stage 2
    conv2 = layers.Conv3D(n_filters*2, kernel_size=3, padding='same')(pool1)
    conv2 = layers.PReLU()(conv2)
    conv2 = layers.Conv3D(n_filters*2, kernel_size=3, padding='same')(conv2)
    conv2 = layers.PReLU()(conv2)
    # Residual connection
    res2 = layers.Conv3D(n_filters*2, kernel_size=1, padding='same')(pool1)
    conv2 = layers.Add()([conv2, res2])
    # Downsampling
    pool2 = layers.Conv3D(n_filters*4, kernel_size=2, strides=2, padding='same')(conv2)
    pool2 = layers.PReLU()(pool2)
    
    # Stage 3
    conv3 = layers.Conv3D(n_filters*4, kernel_size=3, padding='same')(pool2)
    conv3 = layers.PReLU()(conv3)
    conv3 = layers.Conv3D(n_filters*4, kernel_size=3, padding='same')(conv3)
    conv3 = layers.PReLU()(conv3)
    # Residual connection
    res3 = layers.Conv3D(n_filters*4, kernel_size=1, padding='same')(pool2)
    conv3 = layers.Add()([conv3, res3])
    # Downsampling
    pool3 = layers.Conv3D(n_filters*8, kernel_size=2, strides=2, padding='same')(conv3)
    pool3 = layers.PReLU()(pool3)
    
    # Bottom level
    conv4 = layers.Conv3D(n_filters*8, kernel_size=3, padding='same')(pool3)
    conv4 = layers.PReLU()(conv4)
    conv4 = layers.Conv3D(n_filters*8, kernel_size=3, padding='same')(conv4)
    conv4 = layers.PReLU()(conv4)
    # Residual connection
    res4 = layers.Conv3D(n_filters*8, kernel_size=1, padding='same')(pool3)
    conv4 = layers.Add()([conv4, res4])
    
    # Stage 5 - Decoder path
    up5 = layers.Conv3DTranspose(n_filters*4, kernel_size=2, strides=2, padding='same')(conv4)
    up5 = layers.PReLU()(up5)
    concat5 = layers.Concatenate()([up5, conv3])
    conv5 = layers.Conv3D(n_filters*4, kernel_size=3, padding='same')(concat5)
    conv5 = layers.PReLU()(conv5)
    conv5 = layers.Conv3D(n_filters*4, kernel_size=3, padding='same')(conv5)
    conv5 = layers.PReLU()(conv5)
    # Residual connection
    res5 = layers.Conv3D(n_filters*4, kernel_size=1, padding='same')(concat5)
    conv5 = layers.Add()([conv5, res5])
    
    # Stage 6
    up6 = layers.Conv3DTranspose(n_filters*2, kernel_size=2, strides=2, padding='same')(conv5)
    up6 = layers.PReLU()(up6)
    concat6 = layers.Concatenate()([up6, conv2])
    conv6 = layers.Conv3D(n_filters*2, kernel_size=3, padding='same')(concat6)
    conv6 = layers.PReLU()(conv6)
    conv6 = layers.Conv3D(n_filters*2, kernel_size=3, padding='same')(conv6)
    conv6 = layers.PReLU()(conv6)
    # Residual connection
    res6 = layers.Conv3D(n_filters*2, kernel_size=1, padding='same')(concat6)
    conv6 = layers.Add()([conv6, res6])
    
    # Stage 7
    up7 = layers.Conv3DTranspose(n_filters, kernel_size=2, strides=2, padding='same')(conv6)
    up7 = layers.PReLU()(up7)
    concat7 = layers.Concatenate()([up7, conv1])
    conv7 = layers.Conv3D(n_filters, kernel_size=3, padding='same')(concat7)
    conv7 = layers.PReLU()(conv7)
    conv7 = layers.Conv3D(n_filters, kernel_size=3, padding='same')(conv7)
    conv7 = layers.PReLU()(conv7)
    # Residual connection
    res7 = layers.Conv3D(n_filters, kernel_size=1, padding='same')(concat7)
    conv7 = layers.Add()([conv7, res7])
    
    # Output
    outputs = layers.Conv3D(1, kernel_size=1, activation='sigmoid')(conv7)
    
    model = models.Model(inputs=inputs, outputs=outputs)
    return model

# Check input shape from your data
input_shape = X[0].shape
print(f"Input shape: {input_shape}")

# Build model
model = build_vnet(input_shape)

# Compile model with Dice loss
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=1e-4),
    loss=dice_loss,
    metrics=[
        dice_coefficient,
        tf.keras.metrics.Recall(),
        tf.keras.metrics.Precision()
    ]
)

# Model summary
model.summary()

# Define callbacks - modified for training without validation
callbacks = [
    ModelCheckpoint(
        'best_vnet_model_multicluster.h5',
        save_best_only=True,
        monitor='dice_coefficient',
        mode='max'
    ),
    ReduceLROnPlateau(
        monitor='dice_coefficient',
        factor=0.2,
        patience=5,
        min_lr=1e-6,
        mode='max'
    )
]

# Set batch size based on your GPU memory
batch_size = 2

# Train model - using all data without validation
history = model.fit(
    data_generator(X, y, batch_size),
    steps_per_epoch=len(X) // batch_size,
    epochs=100,
    callbacks=callbacks
)

# Function to predict and save segmentation
def predict_and_save(model, image_file, output_file):
    # Load image
    img_nib = nib.load(image_file)
    img_data = img_nib.get_fdata()
    
    # Normalize
    img_data = (img_data - img_data.min()) / (img_data.max() - img_data.min())
    
    # Add batch and channel dimensions
    img_data = np.expand_dims(np.expand_dims(img_data, axis=0), axis=-1)
    
    # Predict
    pred = model.predict(img_data)[0, ..., 0]
    
    # Threshold prediction
    pred_binary = (pred > 0.5).astype(np.float32)
    
    # Create new NIfTI image with original affine and header
    pred_nib = nib.Nifti1Image(pred_binary, img_nib.affine, img_nib.header)
    
    # Save
    nib.save(pred_nib, output_file)
    
    return pred_binary

# Example: Predict on a test image
test_img = all_image_files[0]
output_file = os.path.join(os.path.dirname(test_img), "vnet_prediction_multicluster_" + os.path.basename(test_img))
pred = predict_and_save(model, test_img, output_file)

print(f"Prediction saved to {output_file}")

# Plot training history
plt.figure(figsize=(12, 4))
plt.subplot(121)
plt.plot(history.history['dice_coefficient'])
plt.title('Dice Coefficient')
plt.xlabel('Epoch')
plt.ylabel('Dice Coefficient')

plt.subplot(122)
plt.plot(history.history['loss'])
plt.title('Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')

plt.tight_layout()
plt.savefig('vnet_training_history_multicluster.png')
plt.close()

# Visualization code
def plot_results(image, true_mask, pred_mask, slice_idx):
    plt.figure(figsize=(12, 4))
    
    plt.subplot(131)
    plt.title('Image')
    plt.imshow(image[slice_idx, :, :, 0], cmap='gray')
    
    plt.subplot(132)
    plt.title('True Mask')
    plt.imshow(true_mask[slice_idx, :, :, 0], cmap='viridis')
    
    plt.subplot(133)
    plt.title('Predicted Mask')
    plt.imshow(pred_mask[slice_idx, :, :], cmap='viridis')
    
    plt.tight_layout()
    plt.savefig(f'vnet_result_slice_{slice_idx}_multicluster.png')
    plt.close()

# Example: Plot middle slice of the first image
test_img_data = X[0]
test_mask_data = y[0]
middle_slice = test_img_data.shape[0] // 2

plot_results(test_img_data, test_mask_data, pred, middle_slice)

print("Training completed and results saved.")