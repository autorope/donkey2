#!/usr/bin/env python3
"""
Scripts to drive a donkey 2 car and train a model for it.

Usage:
    train.py [--model=<model>]

Options:
    -h --help        Show this screen.
    --tubs           Path of tubs to use as training.
"""

import os
from donkeypart_keras_behavior_cloning import KerasLinear
from donkeypart_tub import TubGroup



def train(tubs, new_model_path, base_model_path=None, train_split=.08, batch_size=64):
    """
    use the specified data in tub_names to train an artifical neural network
    saves the output trained model as model_name
    """
    X_keys = ['cam/image_array']
    y_keys = ['user/angle', 'user/throttle']

    new_model_path = os.path.expanduser(new_model_path)

    kl = KerasLinear()
    if base_model_path is not None:
        base_model_path = os.path.expanduser(base_model_path)
        kl.load(base_model_path)

    print('tubs')
    tubgroup = TubGroup(tubs)
    train_gen, val_gen = tubgroup.get_train_val_gen(X_keys, y_keys,
                                                    batch_size=batch_size,
                                                    train_frac=train_split)

    total_records = len(tubgroup.df)
    total_train = int(total_records * train_split)
    total_val = total_records - total_train
    print('train: %d, validation: %d' % (total_train, total_val))
    steps_per_epoch = total_train // batch_size
    print('steps_per_epoch', steps_per_epoch)

    kl.train(train_gen,
             val_gen,
             saved_model_path=new_model_path,
             steps=steps_per_epoch,
             train_split=train_split)


if __name__ == "__main__":
    import datetime
    now = datetime.datetime.now()
    now_str = now.strftime("%Y-%m-%d__%H-%M")
    default_model_name = 'model_{}.h5'.format(now_str)

    import argparse
    parser = argparse.ArgumentParser(description='Script to train a Keras behavioral cloning autopilot.')
    parser.add_argument('tubs', metavar='TUBS', type=str, nargs="+",
                        help='space separated paths to tubs to use for training')
    parser.add_argument("--model", type=str, default=default_model_name,
                        help="Percent of data to use for training.")
    parser.add_argument("--base_model", type=str, help="Base model to use.")
    parser.add_argument("--batch_size", type=int, default=64,
                        help="Number of records to evaluate before backpropigating error.")
    parser.add_argument("--train_split", type=float, default=.8,
                        help="Percent of data to use for training.")

    args = parser.parse_args()
    print(args)

    train(args.tubs, args.model, base_model_path=args.base_model,
          batch_size=args.batch_size, train_split=args.train_split)

