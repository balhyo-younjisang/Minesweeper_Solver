from keras.models import Sequential
from keras.layers import Conv2D, Dense, Flatten
from keras.optimizers import Adam


def create_dqn(learn_rate, ROWDIM, COLDIM):
    model = Sequential()
    model.add(Conv2D(64, (3, 3), padding='same', input_shape=(ROWDIM, COLDIM, 9),
                     activation='relu', use_bias=True, data_format='channels_last'))
    model.add(Conv2D(64, (3, 3), padding='same', activation='relu', use_bias=True))
    model.add(Conv2D(64, (3, 3), padding='same', activation='relu', use_bias=True))
    model.add(Flatten())
    model.compile(optimizer=Adam(lr=learn_rate), loss='mse')

    return model
