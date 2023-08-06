import datetime
import glob
import hashlib
import json
import logging
import os
import random
import shutil

import numpy as np
from addict import Dict
from tqdm import tqdm


class PreProcess:
    def __init__(self, path: str):
        self.path = path

    def set_unique_image_id(self, coco, first_id, inplace: bool):
        """
        :param coco: coco json file to be changed
        :param first_id: first image id value
        :param inplace: If it's True create new coco json file to given directory
        :return: coco json file that have unique image id
        """

        old_dic = {}

        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        for img in coco["images"]:
            old_dic[first_id] = img["id"]
            first_id += 1

        new_dict = dict([(value, key) for key, value in old_dic.items()])

        for img in coco["images"]:
            img["id"] = new_dict[img["id"]]
        for ann in coco["annotations"]:
            ann["image_id"] = new_dict[ann["image_id"]]
        if inplace:
            PreProcess.save_coco_file(coco, f"{self.path}/Unique_id_images_{time}")
            log = logging.getLogger()
            log.info(f"New json file created to {self.path}/Unique_id_images_{time}")
        return coco

    def set_unique_class_id(self, coco, first_id: int, b_grounds: bool, inplace: bool):
        """
        :param coco: coco json file to be changed
        :param first_id: first image id value
        :param b_grounds: Boolean variable. İf it's True add backgrounds list
        :param inplace: If it's True create new coco json file to given directory
        :return: coco json file that have unique category id
        """
        old_dic = {}

        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        backgrounds = {"id": 0, "name": "Background", "supercategory": ""}
        for cat in coco["categories"]:
            old_dic[first_id] = cat["id"]
            first_id += 1

        new_dict = dict([(value, key) for key, value in old_dic.items()])

        for cat in coco["categories"]:
            cat["id"] = new_dict[cat["id"]]

        for ann in coco["annotations"]:
            ann["category_id"] = new_dict[ann["category_id"]]

        if b_grounds:
            coco["categories"].insert(0, backgrounds)

        if inplace:
            PreProcess.save_coco_file(coco, f"{self.path}/unique_id_category_{time}")
            log = logging.getLogger()
            log.info(f"New json file created to {self.path}/unique_id_category_{time}")
        return coco

    def set_unique_annotation_id(self, coco, first_id, inplace: bool):
        """
        :param coco: coco json file to be changed
        :param first_id: first image id value
        :param inplace: If it's True create new coco json file to given directory
        :return: coco json file that have unique annotation id
        """

        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        for ann in coco["annotations"]:
            ann["id"] = first_id
            first_id += 1

        if inplace:
            PreProcess.save_coco_file(coco, f"{self.path}/unique_id_annotation_{time}")
            log = logging.getLogger()
            log.info(f"New json file created to {self.path}/unique_id_annotation_{time}")
        return coco

    @staticmethod
    def check_id_unique(coco):
        """
        :param coco: coco json file to be changed
        :return: Check annotations' id, image id and category id
        are unique. İf each id unique
        returns True, otherwise False
        """
        anno = []
        image = []
        category = []
        for ann in coco["annotations"]:
            anno.append(ann["id"])
        for img in coco["images"]:
            image.append(img["id"])
        for cat in coco["categories"]:
            category.append(cat["id"])

        if np.unique(anno).size == len(anno):
            a = True
        else:
            print("Annotations id not unique")
            a = False
        if np.unique(image).size == len(image):
            b = True
        else:
            print("Image id not unique")
            b = False

        if np.unique(category).size == len(category):
            c = True
        else:
            print("Category id not unique")
            c = False

        if a and b and c:
            return True

        else:
            assert not (a and b and c), "Id not unique"

    def extrack_data_by_class_name(self, coco, categories: list, image_path: str):
        """
        :param coco: Coco json file to be changed
        :param categories: List of chosen categories names
        :param image_path: image path of data set
        :return: Exported json file, image save to new folder in given path directory
        """
        items = []
        ann_items = []
        cat_items = []
        img_id = []
        move_list_dir = []
        image_list = []
        for cat in coco["categories"]:
            if cat["name"] in categories:
                items.append(cat["id"])
                cat_items.append(cat)

        for ann in coco["annotations"]:
            if ann["category_id"] in items:
                ann_items.append(ann)
                img_id.append(ann["image_id"])
        img_id = set(img_id)
        for img in coco["images"]:
            if img["id"] in img_id:
                move_list_dir.append(img["file_name"])
                image_list.append(img)

        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        os.makedirs(self.path + f"/extracted_dataset_{time}")

        for image in move_list_dir:
            shutil.copy(
                image_path + f"/{image}", self.path + f"/extracted_dataset_{time}" + f"/{image}",
            )

        coco["images"] = image_list
        coco["annotations"] = ann_items
        coco["categories"] = cat_items
        coco = PreProcess(self.path).set_unique_image_id(coco, 1, False)
        coco = PreProcess(self.path).set_unique_annotation_id(coco, 1, False)
        coco = PreProcess.set_unique_class_id(self, coco, 1, True, False)
        PreProcess.save_coco_file(coco, f"{self.path}/extracted_dataset_{time}")
        log = logging.getLogger()
        log.info(f"Extracted dataset created to {self.path}/extracted_dataset_{time}")
        return coco

    def filter_data_by_class_name(self, coco, categories: list, image_path: str):
        """
        Remove categories by given list category names
        :param coco: Coco json file to be changed
        :param image_path: image path of data set
        :param categories: List of chosen category's names
        :return: Filtered json file and image save to new folder in given path directory
        """
        items = []
        ann_items = []
        cat_items = []
        img_id = []
        move_list_dir = []
        image_list = []
        for cat in coco["categories"]:
            if cat["name"] not in categories:
                items.append(cat["id"])
                cat_items.append(cat)

        for ann in coco["annotations"]:
            if ann["category_id"] in items:
                ann_items.append(ann)
                img_id.append(ann["image_id"])
        img_id = set(img_id)
        for img in coco["images"]:
            if img["id"] in img_id:
                move_list_dir.append(img["file_name"])
                image_list.append(img)

        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        os.makedirs(self.path + f"/filtered_dataset_{time}")

        for image in move_list_dir:
            shutil.copy(
                image_path + f"/{image}", self.path + f"/filtered_dataset_{time}" + f"/{image}",
            )

        coco["images"] = image_list
        coco["annotations"] = ann_items
        coco["categories"] = cat_items
        coco = PreProcess(self.path).set_unique_image_id(coco, 1, False)
        coco = PreProcess(self.path).set_unique_annotation_id(coco, 1, False)
        coco = PreProcess.set_unique_class_id(self, coco, 1, True, False)
        PreProcess.save_coco_file(coco, f"{self.path}/filtered_dataset_{time}")
        log = logging.getLogger()
        log.info(f"Filtered dataset created to {self.path}/filtered_dataset_{time}")
        return coco

    def box2segmentation(self, coco, inplace: bool):
        """
        if boundary box array has a -1 value change to 1,
        if annotations has no segmentation info create segmentation array
        :param coco: Coco json file to be changed
        :param inplace: If it's True create new coco json file to given directory
        :return: new coco that has segmentation points that created by bbox points
        """
        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        for ann in coco["annotations"]:
            x1, y1, x2, y2 = (
                ann["bbox"][0],
                ann["bbox"][1],
                ann["bbox"][2],
                ann["bbox"][3],
            )
            if not ann["segmentation"]:
                ann["segmentation"] = [[x1, y1, x1, (y1 + y2), (x1 + x2), (y1 + y2), (x1 + x2), y1,]]
        if inplace:
            PreProcess.save_coco_file(coco, f"{self.path}/added_segmentation_{time}")
            log = logging.getLogger()
            log.info(f"New json file created to {self.path}/added_segmentation_{time}")
        return coco

    @staticmethod
    def save_coco_file(coco, path_and_filename):
        """
        :param coco: Coco json file to be changed
        :param path_and_filename: Path with name of json file that will be saved.(Without extension .json)
        """
        with open(path_and_filename + ".json", "w") as fp:
            json.dump(coco, fp)

    def remove_duplicate_image_name(self, coco, inplace: bool):
        """
        :param coco: Coco json file to be changed
        :param inplace: If it's True create new coco json file to given directory
        :return: Remove duplicate names from coco file
        """
        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        id_image = []
        filename = []
        remove_list = []
        images = []
        anno = []
        for img in coco["images"]:
            id_image.append(img["id"])
            filename.append(img["file_name"])
        seen = set()
        dupes = [x for x in filename if x in seen or seen.add(x)]
        for img in coco["images"]:
            if img["file_name"] in dupes:
                remove_list.append(img["id"])
                dupes.remove(img["file_name"])

        for img in coco["images"]:
            if not img["id"] in remove_list:
                images.append(img)
        for ann in coco["annotations"]:
            if ann["image_id"] not in remove_list:
                anno.append(ann)

        coco["annotations"] = anno
        coco["images"] = images
        log = logging.getLogger()
        log.info("Deleted duplicate image count = ", len(remove_list))
        if remove_list:
            if inplace:
                PreProcess.save_coco_file(coco, f"{self.path}/removed_duplicated_{time}")
                log.info(f"New json file created to {self.path}/removed_duplicated_{time}")
        else:
            log.info("There is no duplicate name so ur file did not change and not saved to another json file")
        return coco

    @staticmethod
    def create_random_image_name(image_base_name, path):
        code = f"{path}--{image_base_name}"
        hash_object = hashlib.md5(code.encode())
        photo_uuid = hash_object.hexdigest()
        return photo_uuid + ".jpeg"

    def change_image_file_names(self, coco, path: str, inplace: bool):
        """
        :param coco: Coco json file to be changed
        :param path: Path of folder that contains dataset images
        :param inplace: If it's True create new coco json file to given directory
        :return: Remove duplicate names from coco file
        """
        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        if inplace:
            os.makedirs(f"{self.path}/image_name_change_{time}/images")
            os.makedirs(f"{self.path}/image_name_change_{time}/annotations")

        hashname_dict = {}
        for index, img_path in enumerate(glob.glob(os.path.join(path, "*"))):
            basename = os.path.basename(img_path)
            uuid = PreProcess.create_random_image_name(basename, path)
            hashname_dict[basename] = uuid
            if inplace:
                shutil.copy(
                    img_path, f"{self.path}/image_name_change_{time}/images/{basename}",
                )
                os.rename(
                    f"{self.path}/image_name_change_{time}/images/{basename}",
                    os.path.join(f"{self.path}/image_name_change_{time}/images", uuid),
                )
        for image in coco["images"]:
            for key, values in hashname_dict.items():
                if image["file_name"] == str(key):
                    image["file_name"] = values
        if inplace:
            PreProcess.save_coco_file(
                coco, f"{self.path}/image_name_change_{time}/annotations/image_name_change",
            )
            log = logging.getLogger()
            log.info(f"New dataset folder created to {self.path}/image_name_change_{time}")
        return coco

    def remove_segmentation(self, coco, inplace: bool):
        """
        :param coco: Coco json file to be changed
        :param inplace: If it's True create new coco json file to given directory
        :return: new json coco file that has no segmentation
        """
        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        for ann in coco["annotations"]:
            del ann["segmentation"]
        if inplace:
            PreProcess.save_coco_file(coco, f"{self.path}/removed_segmentation_{time}")
            log = logging.getLogger()
            log.info(f"New json file created to {self.path}/removed_segmentation_{time}")
        return coco

    def remove_distorted_bbox(self, coco, inplace: bool):
        """
        :param coco: Coco json file to be changed
        :param inplace: If it's True create new coco json file to given directory
        :return: Remove bbox that has invalid values
        """
        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")
        ann_list: list = []
        count = 0
        for ann in coco["annotations"]:
            if not (
                len(ann["bbox"]) != 4
                or False in [False for p in ann["bbox"] if type(p) != float and type(p) != int]
                or False in [False for p in ann["bbox"] if p < 0]
            ):
                ann_list.append(ann)
            else:
                count += 1
        coco["annotations"] = ann_list
        if inplace:
            if count != 0:
                PreProcess.save_coco_file(coco, f"{self.path}/removed_distorted_bbox_{time}")
                log = logging.getLogger()
                log.info(f"New json file created to {self.path}/removed_distorted_bbox_{time}")
            else:
                log = logging.getLogger()
                log.info("There is no distorted bbox so ur file did not change and saved to another json file")
        return coco

    def reader(self) -> Dict:
        """
        :return: coco json file
        """
        log = logging.getLogger()
        assert os.path.isfile(self.path), log.error(" Invalid json file path.Please check your directory")

        with open(self.path) as f:
            cfg = json.load(f)
            return Dict(cfg)

    @staticmethod
    def train_test_validation_split(
        coco_file_path, image_path: str, test_percent: int, validation_percent: int, out_path: str,
    ):

        time = str(datetime.datetime.now()).split(".")[0].split()
        time = "-".join(time).replace(":", "-")

        exit_path = out_path + f"/data-{time}"

        train = {
            "licenses": [],
            "info": {},
            "categories": [],
            "images": [],
            "annotations": [],
        }
        test = {
            "licenses": [],
            "info": {},
            "categories": [],
            "images": [],
            "annotations": [],
        }
        validation = {
            "licenses": [],
            "info": {},
            "categories": [],
            "images": [],
            "annotations": [],
        }

        (
            random_list,
            img_id_test,
            img_id_train,
            img_id_val,
            list_dir_train,
            list_dir_test,
            list_dir_validation,
            id_train,
        ) = ([], [], [], [], [], [], [], [])
        list_split = [train, test, validation]

        coco = PreProcess(coco_file_path).reader()
        PreProcess.check_id_unique(coco)

        len_ann = len(coco["annotations"])
        len_test = int(len_ann * test_percent / 100)
        len_validation = int(len_ann * validation_percent / 100)
        len_train = len_ann - (len_test + len_validation)

        log = logging.getLogger()
        log.info("Train annotation count :", len_train)
        log.info("Test annotation count :", len_test)
        log.info("Validation annotation count :", len_validation)

        answer = input("Do you want to split annotations?  [yes/ no]: ")
        if any(answer.lower() == f for f in ["no", "n", "0"]):
            test_p = input("Please choose test percent : %")
            val_p = input("Please choose val percent : %")
            return PreProcess.train_test_validation_split(coco_file_path, image_path, int(test_p), int(val_p), out_path)

        for elem in list_split:
            elem["categories"] = coco["categories"]
            elem["licenses"] = coco["licenses"]
            elem["info"] = coco["info"]

        for i in tqdm(range(len_test + len_validation)):
            x = random.randint(0, (len_test + len_validation))
            while x in random_list:
                x = random.randint(0, len(coco["annotations"]) - 1)
            random_list.append(x)

            if i < len_validation:
                validation["annotations"] += [coco["annotations"][x]]
                id_train.append(coco["annotations"][x]["id"])
                img_id_val.append(coco["annotations"][x]["image_id"])
            else:
                test["annotations"] += [coco["annotations"][x]]
                id_train.append(coco["annotations"][x]["id"])
                img_id_test.append(coco["annotations"][x]["image_id"])

        for ann in tqdm(coco["annotations"]):
            if ann["id"] not in id_train:
                train["annotations"] += [ann]
                img_id_train.append(ann["image_id"])

        img_id_test = set(img_id_test)
        img_id_train = set(img_id_train)
        img_id_val = set(img_id_val)

        for img in tqdm(coco["images"]):
            if img["id"] in img_id_train:
                train["images"] += [img]
                list_dir_train.append(img["file_name"])
            if img["id"] in img_id_test:
                test["images"] += [img]
                list_dir_test.append(img["file_name"])
            if img["id"] in img_id_val:
                validation["images"] += [img]
                list_dir_validation.append(img["file_name"])

        os.makedirs(exit_path + "/train/annotations"), os.makedirs(exit_path + "/train/images")
        p = PreProcess(out_path)
        if len_test != 0:
            os.makedirs(exit_path + "/test/images"), os.makedirs(exit_path + "/test/annotations")

            for image in list_dir_test:
                shutil.copy(
                    image_path + f"/{image}", exit_path + "/test/images" + f"/{image}",
                )
            test = p.set_unique_annotation_id(test, 1, False)
            test = p.set_unique_image_id(test, 1, False)
            PreProcess.save_coco_file(test, exit_path + "/test/annotations/" + "test")
        for image in list_dir_train:
            shutil.copy(
                image_path + f"/{image}", exit_path + "/train/images" + f"/{image}",
            )
        train = p.set_unique_annotation_id(train, 1, False)
        train = p.set_unique_image_id(train, 1, False)
        PreProcess.save_coco_file(train, exit_path + "/train/annotations/" + "train")

        if len_validation != 0:
            os.makedirs(exit_path + "/validation/images"), os.makedirs(exit_path + "/validation/annotations")

            for image in list_dir_validation:
                shutil.copy(
                    image_path + f"/{image}", exit_path + "/validation/images" + f"/{image}",
                )
            validation = p.set_unique_annotation_id(validation, 1, False)
            validation = p.set_unique_image_id(validation, 1, False)
            PreProcess.save_coco_file(
                validation, exit_path + "/validation/annotations/" + "validation",
            )
        log.info("Data split Done!")
        log.info(f" Data saved to {exit_path}")

        return train, test, validation
