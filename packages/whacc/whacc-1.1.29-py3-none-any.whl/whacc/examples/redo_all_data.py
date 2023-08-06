import matplotlib.pyplot as plt
from tqdm.auto import tqdm
from imgaug import augmenters as iaa  # optional program to further augment data

from whacc import utils
import numpy as np
from whacc import image_tools
from natsort import natsorted, ns
import pickle
import pandas as pd
import os
import copy
import seaborn as sns
from keras.preprocessing.image import ImageDataGenerator
import h5py

from whacc import utils
import h5py
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from tqdm.contrib import tzip

################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################

def foo_save(name_in, data):
        tmp1 = os.path.dirname(name_in)
        Path(tmp1).mkdir(parents=True, exist_ok=True)
        np.save(name_in, data)
# h5_meta_data = '/Users/phil/Dropbox/Colab data/H5_data/regular/AH0407_160613_JC1003_AAAC_regular.h5'
# h5_frames = '/Users/phil/Dropbox/Colab data/H5_data/3lag/AH0407_160613_JC1003_AAAC_3lag.h5'
# h5_frames = '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS_FINAL_PRED/AH0407_160613_JC1003_AAAC_ALT_LABELS.h5'

border = 80
d_list = ['/Users/phil/Dropbox/Colab data/H5_data/regular/',
          '/Users/phil/Dropbox/Colab data/H5_data/3lag/',
          '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS_FINAL_PRED/',
          '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS']

h5_meta_images_labels = []
for k in d_list:
    sorted_files = natsorted(utils.get_h5s(k), alg=ns.REAL)
    h5_meta_images_labels.append(sorted_files)

cnt = 0
for h5_meta_data, h5_frames, h5_labels2, h5_labels in tqdm(np.asarray(h5_meta_images_labels).T):
    cnt+=1
    print(cnt)
    if cnt >=7:
        h5_meta_data, h5_frames, h5_labels2, h5_labels = str(h5_meta_data), str(h5_frames), str(h5_labels), str(h5_labels2)

        y = image_tools.get_h5_key_and_concatenate(h5_labels, '[0, 1]- (no touch, touch)')
        OG_frame_nums = image_tools.get_h5_key_and_concatenate(h5_meta_data, 'frame_nums')
        images = image_tools.get_h5_key_and_concatenate(h5_frames, 'images')

        end_name = os.path.basename(h5_frames)[:-3]
        save_dir = '/Volumes/GoogleDrive-114825029448473821206/My Drive/LIGHT_GBM/H5_data/3lag_numpy_aug_for_final_LGBM/'
        name = save_dir + '/images/' + end_name
        if not os.path.isfile(name):
            foo_save(name, images)

            name = save_dir + '/frame_nums/' + end_name
            foo_save(name, OG_frame_nums)

            name = save_dir + '/labels/' + end_name
            foo_save(name, y)

        for aug_num in tqdm(range(10)):
            name = save_dir + '/images_AUG_'+ str(aug_num) +'/' + end_name
            if not os.path.isfile(name):
                datagen = ImageDataGenerator(rotation_range=360,  #
                                                width_shift_range=.1,  #
                                                height_shift_range=.1,  #
                                                shear_range=.00,  #
                                                zoom_range=.25,
                                                brightness_range=[0.2, 1.2])  #
                gaussian_noise = iaa.AdditiveGaussianNoise(loc = 0, scale=3)
                num_aug = 1


                aug_img_stack = []
                for image, label in zip(images, y):
                    aug_img, _ = image_tools.augment_helper(datagen, num_aug, 0, image, label)
                    aug_img = gaussian_noise.augment_images(aug_img) # optional
                    aug_img_stack.append(aug_img)

                aug_img_stack = np.squeeze(np.asarray(aug_img_stack))
                foo_save(name, aug_img_stack)
        del images



# RESNET_MODEL = model_maker.load_final_model()
# features = model.predict(x)

################################################################################################
################################################################################################
################################################################################################
############################################################################ ####################
################################################################################################

# def foo_save(name_in, data):
#         tmp1 = os.path.dirname(name_in)
#         Path(tmp1).mkdir(parents=True, exist_ok=True)
#         np.save(name_in, data)
# # h5_meta_data = '/Users/phil/Dropbox/Colab data/H5_data/regular/AH0407_160613_JC1003_AAAC_regular.h5'
# # h5_frames = '/Users/phil/Dropbox/Colab data/H5_data/3lag/AH0407_160613_JC1003_AAAC_3lag.h5'
# # h5_frames = '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS_FINAL_PRED/AH0407_160613_JC1003_AAAC_ALT_LABELS.h5'
#
# border = 80
# d_list = ['/Users/phil/Dropbox/Colab data/H5_data/regular/',
#           '/Users/phil/Dropbox/Colab data/H5_data/3lag/',
#           '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS_FINAL_PRED/',
#           '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS']
#
# h5_meta_images_labels = []
# for k in d_list:
#     sorted_files = natsorted(utils.get_h5s(k), alg=ns.REAL)
#     h5_meta_images_labels.append(sorted_files)
#
# for h5_meta_data, h5_frames, h5_labels2, h5_labels in tqdm(np.asarray(h5_meta_images_labels).T):
#     # for k in [h5_meta_data, h5_frames, h5_labels2, h5_labels]:
#     #     print(os.path.basename(k))
#     # print('______')
#     h5_meta_data, h5_frames, h5_labels2, h5_labels = str(h5_meta_data), str(h5_frames), str(h5_labels), str(h5_labels2)
#
#     # get the 80 border indices and the 3 border indices
#     y = image_tools.get_h5_key_and_concatenate(h5_labels, '[0, 1]- (no touch, touch)')
#
#
#     # y = np.zeros(4001)
#     # y[2000] = 1
#     OG_frame_nums = image_tools.get_h5_key_and_concatenate(h5_meta_data, 'frame_nums')
#     b = utils.inds_around_inds(y, border * 2 + 1)
#     group_inds, result_ind = utils.group_consecutives(b)
#     new_frame_nums = []
#     for tmp2 in group_inds:
#         new_frame_nums.append(len(tmp2))
#
#     OG_frame_nums_cumulative = np.cumsum(OG_frame_nums)
#     trial_ind_1 = []
#     trial_ind_2 = []
#     for k in group_inds:
#         trial_ind_1.append(np.sum(k[0]>=OG_frame_nums_cumulative))
#         trial_ind_2.append(np.sum(k[0]>=OG_frame_nums_cumulative))
#     assert np.all(trial_ind_2 == trial_ind_1), 'there are overlapping images form one video to the next'
#
#
#     images = image_tools.get_h5_key_and_concatenate(h5_frames, 'images')
#     extracted_images = images[np.concatenate(group_inds), :, :, :]
#     del images
#     labels = np.asarray(y)[np.concatenate(group_inds)]
#     end_name = os.path.basename(h5_frames)[:-3]
#     name = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/images/' + end_name
#     foo_save(name, extracted_images)
#     name = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/80_border_inds/' + end_name
#     foo_save(name, group_inds)
#     name = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/frame_nums/' + end_name
#     foo_save(name, new_frame_nums)
#     name = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/labels/' + end_name
#     foo_save(name, labels)
#     del extracted_images
#
#     #
#     # for aug_num in range(10):
#     #     datagen = ImageDataGenerator(rotation_range=360,  #
#     #                                     width_shift_range=.1,  #
#     #                                     height_shift_range=.1,  #
#     #                                     shear_range=.00,  #
#     #                                     zoom_range=.25,
#     #                                     brightness_range=[0.2, 1.2])  #
#     #     gaussian_noise = iaa.AdditiveGaussianNoise(loc = 0, scale=3)
#     #     num_aug = 1
#     #
#     #
#     #     aug_img_stack = []
#     #     # labels_stack = []
#     #     for image, label in tzip(zip(images, labels)):
#     #         aug_img, label_copy = image_tools.augment_helper(datagen, num_aug, 0, image, label)
#     #         aug_img = gaussian_noise.augment_images(aug_img) # optional
#     #         aug_img_stack.append(aug_img)
#     #         # labels_stack.append(label_copy)
#     #     name = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/images_AUG_'+ str(aug_num) +'/' + end_name
#     #
#     #     np.squeeze(np.asarray(aug_img_stack))
#     #     foo_save(name, extracted_images)




################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################

new_keys = 'src_file'  # ull
# src_file - full directory of all source files


ID_keys = ['file_name_nums',
           'frame_nums',
           'in_range',
           'labels',
           'trial_nums_and_frame_nums',
           'full_file_names',]
for key in ID_keys:
    value = image_tools.get_h5_key_and_concatenate(h5_meta_data, key)

    print(key)
    utils.info(value)
    print('________')
    # for k in trial_ind_1:
################################################################################################
################################################################################################
################################################################################################
################################################################################################
################################################################################################
# for k in utils.get_files(bd, '*.npy'):
#     os.rename(k, k.replace('.h5', ''))


bd = '/Users/phil/Dropbox/Colab data/H5_data/3lag_80_border_numpy/'
fold_list = sorted(next(os.walk(bd))[1])

borderINDS_frame_NUMS_images_labels = []
for k in fold_list:
    sorted_files = natsorted(utils.get_files(bd+k, '*.npy'), alg=ns.REAL)
    borderINDS_frame_NUMS_images_labels.append(sorted_files)

for border_inds, frame_nums, images, labels in tqdm(np.asarray(borderINDS_frame_NUMS_images_labels).T):
    # for k in [border_inds, frame_nums, images, labels]:
    #     print(os.path.basename(k))
    # print('______')
    border_inds, frame_nums, images, labels = str(border_inds), str(frame_nums), str(images), str(labels)
    border_inds, frame_nums, images, labels = np.load(border_inds, allow_pickle=True), np.load(frame_nums, allow_pickle=True), np.load(images, allow_pickle=True), np.load(labels, allow_pickle=True)


datagen = ImageDataGenerator(rotation_range=360,  #
                                width_shift_range=.1,  #
                                height_shift_range=.1,  #
                                shear_range=.00,  #
                                zoom_range=.25,
                                brightness_range=[0.2, 1.2])  #
gaussian_noise = iaa.AdditiveGaussianNoise(loc = 0, scale=3)
num_aug = 1

ind = 80
aug_img_stack = []
labels_stack = []
for image, label in tqdm(zip(images, labels)):
    aug_img, label_copy = image_tools.augment_helper(datagen, num_aug, 0, image, label)
    aug_img = gaussian_noise.augment_images(aug_img) # optional
    aug_img_stack.append(aug_img)
    labels_stack.append(label_copy)





h5creator.add_to_h5(aug_img_stack[:, :, :, :], labels_stack)
utils.copy_h5_key_to_another_h5(each_h5, new_H5_file, 'frame_nums', 'frame_nums') # copy the frame nums to the sug files
# combine all the
image_tools.split_h5_loop_segments(combine_list,
                                     [1],
                                     each_h5.split('.h5')[0]+'_AUG.h5',
                                     add_numbers_to_name = False,
                                     set_seed=0,
                                     color_channel=True)




"""
everything about indexing can be done later
just get the images for now 
that mean just get the images for 3 and 80 
upload and start running the 80 through colab
then augment the 3 
then run the 3 augmented 
worry about the labels later tonight  
"""



    """
    loop through group inds 
    assert they are between some value of the loop segments
    
    """


h5 = '/Users/phil/Dropbox/Colab data/H5_data/ALT_LABELS/AH0667_170317_JC1241_AAAA_ALT_LABELS.h5'
utils.print_h5_keys(h5)

import sys
from tqdm.auto import tqdm
import time

def foo():
    for k in tqdm(range(10)):
        time.sleep(.1)
        print(k)

old_stdout = sys.stdout # backup current stdout
sys.stdout = open(os.devnull, "w")
foo()
sys.stdout = old_stdout # reset old stdout
sys.stdout = sys.__stdout__
foo()


