__version__ = '0.1.0'

import os
import cv2
import json
import numpy as np
from pathlib import Path

IMAGES_FOLDER_NAME = 'images'
TIME_SERIES_FOLDER_NAME = 'tseries'
DESC_FOLDER_NAME = 'descriptions'
PARTICLES_FOLDER_NAME = 'particles'

class CygnoDataset():
    def __init__(self, path, cmos="CMOS", desc="DESCRIPTION", part="PARTICLES", pmt="PMT"):

        # Check the path is not None
        if path is None:
            raise ValueError("The value of path can't be None")

        # Create all directories if there aren't
        p = Path(path)
        p.mkdir(parents=True, exist_ok=True)

        # Check the given path for an existing dataset
        if not self._dataset_exists_on_path(p):
            #TODO: Add an auto download dataset function here 
            raise ValueError(f"No valid dataset was found on {path}.")
            

    def _dataset_exists_on_path(self, path):

        # Checks if a folder exists and is not empty
        def folder_there_and_not_empty(base_path, folder_name, ignore_empty=False):
            folder_path = base_path / folder_name
            if folder_path.exists() and folder_path.is_dir():
                if ignore_empty or any(folder_path.iterdir()):
                    return folder_path

        # Check all the subfolders
        self.cmos_path = folder_there_and_not_empty(path, IMAGES_FOLDER_NAME)
        self.pmt_path = folder_there_and_not_empty(path, TIME_SERIES_FOLDER_NAME, ignore_empty=True)
        self.desc_path = folder_there_and_not_empty(path, DESC_FOLDER_NAME)
        self.particles_path = folder_there_and_not_empty(path, PARTICLES_FOLDER_NAME)
        self.path = path
        
        return bool(self.cmos_path and self.pmt_path and self.desc_path and self.particles_path)
    
    def load_experiment(self, experiment_id):
        trajs, t_classes = self.load_experiment_trajs(experiment_id=experiment_id)
        cmos = self.load_experiment_cmos(experiment_id=experiment_id)
        pmt = self.load_experiment_pmt(experiment_id=experiment_id)
        return trajs, t_classes, cmos, pmt
    
    def load_experiment_description(self, experiment_id):
        desc_path = os.path.join(self.desc_path, f"{experiment_id}.json")
        with open(desc_path, encoding="utf-8") as json_file:
            desc = json.load(json_file)
        return desc

    def load_traj(self, p_file):
        p = np.loadtxt(p_file, ndmin=2)
        return p

    def load_experiment_trajs(self, experiment_id):
        desc = self.load_experiment_description(experiment_id)
        particles, p_types = [], []
        for p in desc["particles_info"]:
            p_file = os.path.join(self.path, p["file"])
            particles.append(self.load_traj(p_file))
            p_types.append(p["type"])
        return particles, p_types
    
    def load_experiment_cmos(self, experiment_id):
        image_path = os.path.join(self.cmos_path, f"{experiment_id}.png")
        return cv2.imread(image_path)
    
    def load_experiment_pmt(self, experiment_id):
        pmt_path = os.path.join(self.pmt_path, f"{experiment_id}.npy")
        try:
            return np.load(pmt_path)
        except FileNotFoundError:
            return None

    def load_all_trajs(self):
        experiment_ids = self.list_all_experiments()
        p, p_type = [], []
        for e_id in experiment_ids:
            pi, pti = self.load_experiment_trajs(e_id)
            p += pi
            p_type += pti
        return p, p_type

    def load_all_cmos(self):
        experiment_ids = self.list_all_experiments()
        all_cmos = []
        for e_id in experiment_ids:
            c_cmos = self.load_experiment_cmos(e_id)
            all_cmos.append(c_cmos)
        return all_cmos

    def load_all_pmt(self):
        experiment_ids = self.list_all_experiments()
        all_pmt = []
        for e_id in experiment_ids:
            c_pmt = self.load_experiment_pmt(e_id)
            all_pmt.append(c_pmt)
        return all_pmt

    def list_all_experiments(self):
        return [ex.split('.')[0]  for ex in os.listdir(self.desc_path) if 'json' in ex]