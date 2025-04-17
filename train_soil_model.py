import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
import numpy as np

# Generate Dummy Data (Replace with real soil data if available)
num_samples = 500
X_train = np.random.rand(num_samples, 4)  # Example Features: pH, Moisture, etc.
y_train = np.random.randint(0, 2, num_samples)  # Binary categories (0 = Not Suitable, 1 = Suitable)

# Define the Model
model = Sequential([
    Dense(16, activation='relu', input_shape=(4,)),
    Dense(8, activation='relu'),
    Dense(1, activation='sigmoid')  # Binary classification
])

# Compile the Model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the Model
model.fit(X_train, y_train, epochs=5, batch_size=32, verbose=1)

# Save the Model
model.save("soil_model.h5")

print("✅ Model saved successfully as 'soil_model.h5'")
