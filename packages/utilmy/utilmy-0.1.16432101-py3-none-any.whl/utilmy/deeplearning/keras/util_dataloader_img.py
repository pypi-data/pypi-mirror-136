# -*- coding: utf-8 -*-
HELP = """
 utils keras for dataloading
"""
import os,io, numpy as np, sys, glob, time, copy, json, pandas as pd, functools, sys
import cv2
import tensorflow as tf
# import tifffile.tifffile
# from skimage import morphology
import PIL
from PIL import Image
from albumentations import (
    Compose, HorizontalFlip, CLAHE, HueSaturationValue,
    RandomBrightness, RandomContrast, RandomGamma,
    ToFloat, ShiftScaleRotate, Resize
)
from albumentations.core.transforms_interface import ImageOnlyTransform



###################################################################################################
from utilmy import log, log2

def help():
    from utilmy import help_create
    ss = HELP + help_create("utilmy.deeplearning.keras.util_layers")
    print(ss)


###################################################################################################    
def test():    
  #image_size = 64
  train_augments = Compose([
      #Resize(image_size, image_size, p=1),
      HorizontalFlip(p=0.5),
      #RandomContrast(limit=0.2, p=0.5),
      #RandomGamma(gamma_limit=(80, 120), p=0.5),
      #RandomBrightness(limit=0.2, p=0.5),
      #HueSaturationValue(hue_shift_limit=5, sat_shift_limit=20,
      #                   val_shift_limit=10, p=.9),
      ShiftScaleRotate(
          shift_limit=0.0625, scale_limit=0.1, 
          rotate_limit=15, border_mode=cv2.BORDER_REFLECT_101, p=0.8), 
      # ToFloat(max_value=255),
      Transform_sprinkle(p=0.5),
  ])

  test_augments = Compose([
      # Resize(image_size, image_size, p=1),
      # ToFloat(max_value=255)
  ])

  ###############################################################################
  image_size =  64
  train_transforms = Compose([
      Resize(image_size, image_size, p=1),
      HorizontalFlip(p=0.5),
      RandomContrast(limit=0.2, p=0.5),
      RandomGamma(gamma_limit=(80, 120), p=0.5),
      RandomBrightness(limit=0.2, p=0.5),
      HueSaturationValue(hue_shift_limit=5, sat_shift_limit=20,
                         val_shift_limit=10, p=.9),
      ShiftScaleRotate(
          shift_limit=0.0625, scale_limit=0.1, 
          rotate_limit=15, border_mode=cv2.BORDER_REFLECT_101, p=0.8), 
      ToFloat(max_value=255),
      Transform_sprinkle(num_holes=10, side_length=10, p=0.5),
  ])

  test_transforms = Compose([
      Resize(image_size, image_size, p=1),
      ToFloat(max_value=255)
  ])
  




def test1():
    from tensorflow.keras.datasets import mnist

    (X_train, y_train), (X_valid, y_valid) = mnist.load_data()

    train_loader = DataGenerator_img(X_train, y_train)

    for i, (image, label) in enumerate(train_loader):
        print('Training : ')
        print(f'image shape : {image.shape}')
        print(f'label shape : {label.shape}')
        break



def test2(): #using predefined df and model training using model.fit()
    from PIL import Image
    from pathlib import Path
    from tensorflow import keras
    from tensorflow.keras import layers

    def get_model():
      model = keras.Sequential(  [
        keras.Input(shape=(28, 28, 3)),
        layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
        layers.MaxPooling2D(pool_size=(2, 2)),
        layers.Flatten(),
        layers.Dense(num_labels, activation="softmax"),
      ] )
      model.compile(loss=tf.keras.losses.CategoricalCrossentropy(), 
                  optimizer=tf.keras.optimizers.Adam(learning_rate=1e-7), 
                  metrics=["accuracy"])
      return model

    folder_name = 'random_images'
    csv_file_name = 'df.csv'
    p = Path(folder_name)
    num_images = 256
    num_labels = 2

    df = create_random_images_ds((28, 28, 3), num_images = num_images, num_labels = num_labels, folder = folder_name)

    #df = create_random_images_ds2(img_shape=(10,10,2), num_images = 10,
    #                              dirout =folder_name,  n_class_perlabel=2,  cols_labels = [ 'gender', ] )
    df.to_csv(csv_file_name, index=False)



    log('############   without Transform')
    dt_loader = DataGenerator_img_disk(p.as_posix(), df, ['label'], batch_size = 32)

    for i, (image, label) in enumerate(dt_loader):
        log(f'image shape : {(image).shape}')
        log(f'label shape : {(label).shape}')
        break

    model = get_model()
    model.fit(
        dt_loader,
        epochs=5,
    )

    log('############   with Transform')
    trans_train = Compose([
      #Resize(image_size, image_size, p=1),
      HorizontalFlip(p=0.5),
      #RandomContrast(limit=0.2, p=0.5),
      #RandomGamma(gamma_limit=(80, 120), p=0.5),
      #RandomBrightness(limit=0.2, p=0.5),
      #HueSaturationValue(hue_shift_limit=5, sat_shift_limit=20,
      #                   val_shift_limit=10, p=.9),
      ShiftScaleRotate(
          shift_limit=0.0625, scale_limit=0.1,
          rotate_limit=15, border_mode=cv2.BORDER_REFLECT_101, p=0.8),
      # ToFloat(max_value=255),
      Transform_sprinkle(p=0.5),
     ])
    dt_loader = DataGenerator_img_disk(p.as_posix(), label_dir= df, label_cols= ['label'], batch_size = 32, col_img='uri', transforms= trans_train )

    for i, (image, label) in enumerate(dt_loader):
        log(f'image shape : {(image).shape}')
        log(f'label shape : {(label).shape}')
        break
    
    model = get_model()
    model.fit(
        dt_loader,
        epochs=5,
    )

def create_random_images_ds(img_shape, num_images = 10, folder = 'random images', return_df = True, num_labels = 2, label_cols = ['label']):
        if not os.path.exists(folder):
            os.mkdir(folder)
        for n in range(num_images):
            filename = f'{folder}/{n}.jpg'
            rgb_img = np.random.rand(img_shape[0],img_shape[1],img_shape[2]) * 255
            image = Image.fromarray(rgb_img.astype('uint8')).convert('RGB')
            image.save(filename)

        label_dict = []

        files = [i.as_posix() for i in p.glob('*.jpg')]
        for i in enumerate(label_cols):
            label_dict.append(np.random.randint(num_labels, size=(num_images)))

        df = pd.DataFrame(list(zip(files, *label_dict)), columns=['uri'] + label_cols)
        if return_df:
            return df


def create_random_images_ds2(img_shape=(10,10,2), num_images = 10,
                            dirout ='random_images/',  n_class_perlabel=7,  cols_labels = [ 'gender', 'color', 'size'] ):
    """ Image + labels into Folder + csv files.
        Multiple label:
    """
    os.makedirs(dirout, exist_ok=True)
    for n in range(num_images):
        filename = f'{dirout}/{n}.jpg'
        rgb_img  = np.random.rand(img_shape[0],img_shape[1],img_shape[2]) * 255
        image    = Image.fromarray(rgb_img.astype('uint8')).convert('RGB')
        image.save(filename)


    files = [fi.replace("\\", "/") for fi in glob.glob( dirout + '/*.jpg')]
    df = pd.DataFrame(files, columns=['img_dir'])

 

##################################################################################################
def get_data_sample(batch_size, x_train, labels_val, labels_col):   #name changed
    """ Get a data sample with batch size from dataset
    Args:
        batch_size (int): Provide a batch size for sampling
        x_train (list): Inputs from the dataset
        labels_val (list): True labels for the dataset
        labels_col(list): Samples to select from these columns

    Returns:
        x (numpy array): Selected samples of size batch_size
        y_label_list (list): List of labels from selected samples  
        
    """
    #### 
    # i_select = 10
    # i_select = np.random.choice(np.arange(train_size), size=batch_size, replace=False)
    i_select = np.random.choice(np.arange(len(labels_val['gender'])), size=batch_size, replace=False)


    #### Images
    x        = np.array([ x_train[i]  for i in i_select ] )

    #### y_onehot Labels  [y1, y2, y3, y4]
    # labels_col   = [  'gender', 'masterCategory', 'subCategory', 'articleType' ] #*To make user-defined
    y_label_list = []
    for ci in labels_col :
        v =  labels_val[ci][i_select]
        y_label_list.append(v)

    return x, y_label_list 


def pd_get_onehot_dict(df, labels_col:list, dfref=None, ) :       #name changed
    """

    Args:
        df (DataFrame): Actual DataFrame
        dfref (DataFrame): Reference DataFrame 
        labels_col (list): List of label columns

    Returns:
        dictionary: label_columns, count
    """
    if dfref is not None :
        df       = df.merge(dfref, on = 'id', how='left')

    
    labels_val = {}
    labels_cnt = {}
    for ci in labels_col:
      dfi_1hot  = pd.get_dummies(df, columns=[ci])  ### OneHot
      dfi_1hot  = dfi_1hot[[ t for t in dfi_1hot.columns if ci in t   ]].values  ## remove no OneHot
      labels_val[ci] = dfi_1hot 
      labels_cnt[ci] = df[ci].nunique()
      assert dfi_1hot.shape[1] == labels_cnt[ci],   labels_cnt     
    
    print(labels_cnt)
    return labels_val, labels_cnt
    
    

def pd_merge_labels_imgdir(dflabels, img_dir="*.jpg", labels_col = []) :   #name changed
    """One Hot encode label_cols
    # 
    #    id, uri, cat1, cat2, .... , cat1_onehot
    #
    Args:
        dflabels (DataFrame): DataFrame to perform one hot encoding on
        img_dir (Path(str)): String Path /*.png to image directory
        labels_col (list): Columns to perform One Hot encoding on. Defaults to []

    Returns:
        DataFrame: One Hot encoded DataFrame
    """

    import glob
    fpaths   = glob.glob(img_dir )
    fpaths   = [ fi for fi in fpaths if "." in fi.split("/")[-1] ]
    log(str(fpaths)[:100])

    df         = pd.DataFrame(fpaths, columns=['uri'])
    log(df.head(1).T)
    df['id']   = df['uri'].apply(lambda x : x.split("/")[-1].split(".")[0]    )
    # df['id']   = df['id'].apply( lambda x: int(x) )
    df         = df.merge(dflabels, on='id', how='left')

    # labels_col = [  'gender', 'masterCategory', 'subCategory', 'articleType' ]
    for ci in labels_col :
      dfi_1hot           = pd.get_dummies(df, columns=[ci])  ### OneHot
      dfi_1hot           = dfi_1hot[[ t for t in dfi_1hot.columns if ci in t   ]]  ## keep only OneHot
      df[ci + "_onehot"] = dfi_1hot.apply( lambda x : ','.join([   str(t) for t in x  ]), axis=1)
      #####  0,0,1,0 format   log(dfi_1hot)
    return df


def pd_to_onehot(dflabels, labels_col = []) :   #name changed
    """One Hot encode label_cols for predefined df
    #    id, uri, cat1, cat2, .... , cat1_onehot
    Args:
        dflabels (DataFrame): DataFrame to perform one hot encoding on
        labels_col (list): Columns to perform One Hot encoding on. Defaults to []

    Returns:
        DataFrame: One Hot encoded DataFrame
    """
    for ci in labels_col :
      dfi_1hot           = pd.get_dummies(dflabels, columns=[ci])  ### OneHot
      dfi_1hot           = dfi_1hot[[ t for t in dfi_1hot.columns if ci in t   ]]  ## keep only OneHot
      dflabels[ci + "_onehot"] = dfi_1hot.apply(lambda x : ','.join([str(t) for t in x]), axis=1)
      #####  0,0,1,0 format   log(dfi_1hot)

    return dflabels


                            
###############################################################################
from albumentations.core.transforms_interface import ImageOnlyTransform
class Transform_sprinkle(ImageOnlyTransform):
    def __init__(self, num_holes=30, side_length=5, always_apply=False, p=1.0):
        from tf_sprinkles import Sprinkles
        super(Transform_sprinkle, self).__init__(always_apply, p)
        self.sprinkles = Sprinkles(num_holes=num_holes, side_length=side_length)
    
    def apply(self, image, **params):
        if isinstance(image, PIL.Image.Image):   image = tf.constant(np.array(image), dtype=tf.float32)            
        elif isinstance(image, np.ndarray):      image = tf.constant(image, dtype=tf.float32)
        return self.sprinkles(image).numpy()

    

def transform_get_basic(pars:dict=None):    
  """"  Get Transformation Class for Datalaoder
        Basic version
  cc.resize.p = 1
  
  """
  cc = Box({}) if pars is None else Box(pars)

  cc.height = 64
  cc.width  = 64
  
  train_transforms = Compose([
      Resize(cc.height, cc.width, p=1),
      HorizontalFlip(p=0.5),
      RandomContrast(limit=0.2, p=0.5),
      RandomGamma(gamma_limit=(80, 120), p=0.5),
      RandomBrightness(limit=0.2, p=0.5),
      HueSaturationValue(hue_shift_limit=5, sat_shift_limit=20,
                         val_shift_limit=10, p=.9),
      ShiftScaleRotate(
          shift_limit=0.0625, scale_limit=0.1, 
          rotate_limit=15, border_mode=cv2.BORDER_REFLECT_101, p=0.8), 
      ToFloat(max_value=255),
      Transform_sprinkle(num_holes=10, side_length=10, p=0.5),
  ])

  test_transforms = Compose([
      Resize(cc.height, cc.width, p=1),
      ToFloat(max_value=255)
  ])
  return train_transforms, test_transforms
    
    
    
##########################################################################################
class CustomDataGenerator(Sequence):
    """Custom DataGenerator using keras Sequence
    Args: x (np array): The input samples from the dataset
          y (np array): The labels from the dataset
          batch_size (int, optional): batch size for the samples. Defaults to 32.
          augmentations (str, optional): perform augmentations to the input samples. Defaults to None.
    """
    
    def __init__(self, x, y, batch_size=32, augmentations=None):
        self.x          = x
        self.y          = y
        self.batch_size = batch_size
        self.augment    = augmentations

    def __len__(self):
        return int(np.ceil(len(self.x) / float(self.batch_size)))

    def __getitem__(self, idx):
        batch_x = self.x[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_y = self.y[idx * self.batch_size:(idx + 1) * self.batch_size]
        # for y_head in self.y:                                                         ----
        #     batch_y.append(y_head[idx * self.batch_size:(idx + 1) * self.batch_size]) ----
        if self.augment is not None:
            batch_x = np.stack([self.augment(image=x)['image'] for x in batch_x], axis=0)
        # return (batch_x, *batch_y)                                                    ----
        return (batch_x, batch_y)

    
    
#################################################################################   
class DataGenerator_img_disk(tf.keras.utils.Sequence):
    """Custom DataGenerator using Keras Sequence for images on disk
        df_label format :
        id, uri, cat1, cat2, cat3, cat1_onehot, cat1_onehot, ....
        Args:
            img_dir (Path(str)): String path to images directory
            label_dir (DataFrame): Dataset for Generator
            label_cols (list): list of cols for the label (multi label)
            split (str, optional): split for train or test. Defaults to 'train'.
            batch_size (int, optional): batch_size for each batch. Defaults to 8.
            transforms (str, optional):  type of transformations to perform on images. Defaults to None.
    """

    def __init__(self, img_dir, label_dir, label_cols:list,  split='train', col_img='uri', batch_size=8, transforms=None):
        self.image_dir  = img_dir
        self.batch_size = batch_size
        self.transforms = transforms


        self.label_cols = label_cols
        self.col_img = col_img

        from utilmy import pd_read_file
        dflabel     = pd_read_file(label_dir)
        dflabel     = dflabel.dropna()
        self.labels = pd_to_onehot(dflabel, label_cols)


        assert col_img in self.labels.columns


    def on_epoch_end(self):
        np.random.seed(12)
        self.labels = self.labels.sample(frac=1).reset_index(drop=True)
        # np.random.shuffle(self.labels.reset_index(drop=True))

    def __len__(self):
        return int(np.ceil(len(self.labels) / float(self.batch_size)))

    def __getitem__(self, idx):
        # Create batch targets
        # df_batch    = self.labels[idx * self.batch_size:(idx + 1) * self.batch_size]

        # batch_x = []
        # batch_y = []  #  list of heads

        # for ii, x in df_batch.iterrows():
        #     img =  np.array(Image.open(x[ self.col_img]).convert('RGB') )
        #     batch_x.append(img)

        # for ci in self.label_cols:
        #     v = [x.split(",") for x in df_batch[ci + "_onehot"]]
        #     v = np.array([[int(t) for t in vlist] for vlist in v])
        #     batch_y.append(v)

        # if self.transforms is not None:
        #     batch_x = np.stack([self.transforms(image=x)['image'] for x in batch_x], axis=0)

        batch_x, batch_y = self.__get_data(idx, self.batch_size)

        return np.array(batch_x), np.array(batch_y)


    def __get_data(self, idx, batch=8):
        # Create batch targets
        df_batch    = self.labels[idx * batch:(idx + 1) * self.batch_size]

        batch_x = []
        batch_y = []  #  list of heads

        for ii, x in df_batch.iterrows():
            img =  np.array(Image.open(x['uri']).convert('RGB') )
            batch_x.append(img)

        for ci in self.label_cols:
            v = [x.split(",") for x in df_batch[ci + "_onehot"]]
            v = np.array([[int(t) for t in vlist] for vlist in v])
            batch_y.append(v)

        if self.transforms is not None:
            batch_x = np.stack([self.transforms(image=x)['image'] for x in batch_x], axis=0)

        return (batch_x, *batch_y)


 
class Dataloader_img_disk_custom(tf.keras.utils.Sequence):
    """Custom Data Loader using keras Sequence
        Args:  image_dir (Path(str)): String Path /*.png to image directory
               label_path (DataFrame): Dataset for Generator
               class_dict (list): list of columns for categories
               split (str, optional): split as train, validation, or test. Defaults to 'train'.
               batch_size (int, optional): Batch size for the dataloader. Defaults to 8.
               transforms (str, optional): type of transform to perform on images. Defaults to None.
               shuffle (bool, optional): Shuffle the data. Defaults to True.
        """
        
    def __init__(self, image_dir, label_path, class_dict,
                 split='train', batch_size=8, transforms=None, shuffle=True):
        self.image_dir = image_dir
        # self.labels = np.loadtxt(label_dir, delimiter=' ', dtype=np.object)
        self.class_dict = class_dict
        self.image_ids, self.labels = self._load_data(label_path)
        self.num_classes = len(class_dict)
        self.batch_size = batch_size
        self.transforms = transforms
        self.shuffle = shuffle

    def _load_data(self, label_path):
        df = pd.read_csv(label_path, error_bad_lines=False, warn_bad_lines=False)
        keys = ['id'] + list(self.class_dict.keys())
        df = df[keys]

        # Get image ids
        df = df.dropna()
        image_ids = df['id'].tolist()
        df = df.drop('id', axis=1)
        labels = []
        for col in self.class_dict:
            categories = pd.get_dummies(df[col]).values
            labels.append(categories)
        return image_ids, labels

    def on_epoch_end(self):
        if self.shuffle:
            np.random.seed(12)
            indices = np.arange(len(self.image_ids))
            np.random.shuffle(indices)
            self.image_ids = self.image_ids[indices]
            self.labels = [label[indices] for label in self.labels]

    def __len__(self):
        return int(np.ceil(len(self.image_ids) / float(self.batch_size)))

    def __getitem__(self, idx):
        batch_img_ids = self.image_ids[idx * self.batch_size:(idx + 1) * self.batch_size]
        batch_x = []
        for image_id in batch_img_ids:
            # Load image
            image = np.array(Image.open(os.path.join(self.image_dir, '%d.jpg' % image_id)).convert('RGB'))
            batch_x.append(image)

        batch_y = []
        for y_head in self.labels:
            batch_y.append(y_head[idx * self.batch_size:(idx + 1) * self.batch_size, :])

        if self.transforms is not None:
            batch_x = np.stack([self.transforms(image=x)['image'] for x in batch_x], axis=0)
        return (idx, batch_x, *batch_y)


def _byte_feature(value):
    if not isinstance(value, (tuple, list)):
        value = [value]
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=value))


def _int64_feature(value):
    if not isinstance(value, (tuple, list)):
        value = [value]
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


def _float_feature(value):
    if not isinstance(value, (tuple, list)):
        value = [value]
    return tf.train.Feature(float_list=tf.train.FloatList(value=value))


def build_tfrecord(x, tfrecord_out_path, max_records):
    extractor = tf.keras.applications.ResNet50V2(
        include_top=False, weights='imagenet',
        input_shape=(xdim, ydim, cdim),
        pooling='avg'
    )
    with tf.io.TFRecordWriter(tfrecord_out_path) as writer:
        id_cnt = 0
        for i, (_, images, *_) in enumerate(x):
            if i > max_records:
                break
            batch_embedding = extractor(images, training=False).numpy().tolist()
            for embedding in batch_embedding:
                example = tf.train.Example(features=tf.train.Features(feature={
                    'id': _byte_feature(str(id_cnt).encode('utf-8')),
                    'embedding': _float_feature(embedding),
                }))
                writer.write(example.SerializeToString())
                id_cnt += 1
    return tfrecord_out_path

   
   
