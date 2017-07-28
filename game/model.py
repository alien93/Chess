from keras.models import Sequential
from keras.layers import Dense, Activation, LSTM, Dropout
import time 

def build_model():
    model = Sequential()
    model.add(Dense(512, input_dim=256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(768, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(512, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(1, activation='sigmoid'))

    start = time.time()
    model.compile(loss='binary_crossentropy',
              optimizer='rmsprop',
              metrics=['accuracy'])    
    print "Compilation Time : ", time.time() - start
    return model