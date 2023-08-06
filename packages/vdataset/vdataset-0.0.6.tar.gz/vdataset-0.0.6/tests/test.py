import sys

sys.path.append( 'C:\\CODE\\vdataset' )

from vdataset.vdataset import VDataset
from vdataset.labelmap import LabelMap
import torch
from torchvideotransforms import video_transforms, volume_transforms

# DEVICE SELECTING
DEVICE = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print("Executing on: {}".format(DEVICE))

# CONSTANTS GOES HERE
FRAME_SIZE = (224, 224)

DATASET_ROOT = "C:\\CODE\\GI-RESNET3D\\data\\20BN-JESTER"
CSV_PATH = {
    "train": "{}/Train.csv".format(DATASET_ROOT),
    "validation": "{}/Test.csv".format(DATASET_ROOT)
    }

DATA_DIR = {
    "train": "{}/Train".format(DATASET_ROOT),
    "validation" : "{}/Validation".format(DATASET_ROOT)
    }


labelMap = LabelMap(labels_csv=CSV_PATH["train"], labels_col_name='label')
labelMap.print()

transforms = {
    "train": video_transforms.Compose([video_transforms.RandomRotation(30), 
              video_transforms.Resize(FRAME_SIZE), 
              volume_transforms.ClipToTensor()]),
    "validation": video_transforms.Compose([video_transforms.Resize(FRAME_SIZE), 
                                            volume_transforms.ClipToTensor()])
}


datasets = {
    "train": VDataset(csv_file=CSV_PATH["train"], root_dir=DATA_DIR['train'], video_transforms=transforms["train"], label_map=labelMap, frames_limit_mode="manual", frames_limit={"start": 5, "end": -5},),
    "validation": VDataset(csv_file=CSV_PATH["validation"], root_dir=DATA_DIR['validation'], video_transforms=transforms["validation"], label_map=labelMap),
}

dataloaders = {
    "train": torch.utils.data.DataLoader(datasets["train"], batch_size=16, shuffle=False, pin_memory=True),
    "validation": torch.utils.data.DataLoader(datasets["validation"], batch_size=16, shuffle=False, pin_memory=True)
}
print(dataloaders)


for i, data in enumerate(dataloaders['train']):
    print("Batch : {} ".format(i))
    imgs, labels = data
    print(imgs.size())
    print(labels)
    break;
