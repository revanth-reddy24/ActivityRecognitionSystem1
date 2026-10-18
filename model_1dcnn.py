import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (Input, Conv1D, MaxPooling1D, Flatten, 
                                     Dense, Dropout, Concatenate, BatchNormalization)
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical


# classes = 6  (walking, standing, fall, sitting, running, lying)

samples = 2000
time_steps = 100
subcarriers = 128
num_classes = 6

csi_complex = np.load("your_csi_file.npy")    

# Extract real, imaginary, and amplitude
X_real = np.real(csi_complex)
X_imag = np.imag(csi_complex)
X_abs  = np.abs(csi_complex)

# Labels (dummy)
y = np.random.randint(0, num_classes, samples)
y = to_categorical(y, num_classes)


# ============================================================
# 2. TRAIN–TEST SPLIT
# ============================================================

X_real_train, X_real_test, \
X_imag_train, X_imag_test, \
X_abs_train, X_abs_test, \
y_train, y_test = train_test_split(X_real, X_imag, X_abs, y, 
                                   test_size=0.2, random_state=42)


# ============================================================
# 3. CNN FEATURE EXTRACTION BLOCK
# ============================================================

def cnn_block(input_tensor):
    x = Conv1D(64, kernel_size=3, activation='relu', padding='same')(input_tensor)
    x = BatchNormalization()(x)
    x = MaxPooling1D(pool_size=2)(x)

    x = Conv1D(128, kernel_size=3, activation='relu', padding='same')(x)
    x = BatchNormalization()(x)
    x = MaxPooling1D(pool_size=2)(x)

    x = Flatten()(x)
    return x


# ============================================================
# 4. CREATE MULTI-CHANNEL INPUT LAYERS
# ============================================================

real_input = Input(shape=(time_steps, subcarriers), name="real_input")
imag_input = Input(shape=(time_steps, subcarriers), name="imag_input")
abs_input  = Input(shape=(time_steps, subcarriers), name="abs_input")


# ============================================================
# 5. EXTRACT FEATURES FROM EACH CHANNEL
# ============================================================

real_features = cnn_block(real_input)
imag_features = cnn_block(imag_input)
abs_features  = cnn_block(abs_input)


# ============================================================
# 6. CONCATENATE CHANNEL FEATURES
# ============================================================

combined = Concatenate()([real_features, imag_features, abs_features])


# ============================================================
# 7. CLASSIFICATION HEAD
# ============================================================

x = Dense(256, activation='relu')(combined)
x = Dropout(0.5)(x)
x = Dense(128, activation='relu')(x)
x = Dropout(0.3)(x)

output = Dense(num_classes, activation='softmax')(x)



model = Model(inputs=[real_input, imag_input, abs_input], outputs=output)

model.summary()


# ============================================================
# 9. COMPILE THE MODEL
# ============================================================

model.compile(
    optimizer='adam',
    loss='categorical_crossentropy',
    metrics=['accuracy']
)


# ============================================================
# 10. TRAIN THE MODEL
# ============================================================

history = model.fit(
    [X_real_train, X_imag_train, X_abs_train],
    y_train,
    batch_size=32,
    epochs=30,
    validation_split=0.2
)




loss, accuracy = model.evaluate([X_real_test, X_imag_test, X_abs_test], y_test)
print("\nTest Accuracy:", accuracy)



model.save("WiCNNAct_model.h5")
print("\nModel saved as WiCNNAct_model.h5")
