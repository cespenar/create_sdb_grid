import os
import shutil
from zipfile import ZipFile

import numpy as np


class Progenitor:

    grid_file = '/home/jomesa/sdb/progenitors/grid_progenitors_20201005.txt'
    grid = np.genfromtxt(grid_file, dtype=None, names=True)

    def __init__(self, m_i, z, level, rot=0.0, fh=0.0,
                 fhe=0.0, fsh=0.0, mlt=1.8, sc=0.1, reimers=0.0, blocker=0.0, turbulence=0.0):
        self.m_i = m_i
        self.z = z
        self.level = level
        self.rot = rot
        self.fh = fh
        self.fhe = fhe
        self.fsh = fsh
        self.mlt = mlt
        self.sc = sc
        self.reimers = reimers
        self.blocker = blocker
        self.turbulence = turbulence

        selected_progenitor = self.select_progenitor()

        self.model_number = int(selected_progenitor['model_number'])
        self.y = selected_progenitor['y']
        self.m = selected_progenitor['m']
        self.log_Teff = selected_progenitor['log_Teff']
        self.log_L = selected_progenitor['log_L']
        self.age = selected_progenitor['age']
        self.m_core = selected_progenitor['m_core']

        self.progenitor_name = selected_progenitor()

    def select_progenitor(self):
        condition = \
            (self.grid['m_i'] == self.m_i) & \
            (self.grid['z'] == self.z) & \
            (self.grid['level'] == self.level) & \
            (self.grid['rot'] == self.rot) & \
            (self.grid['fh'] == self.fh) & \
            (self.grid['fhe'] == self.fhe) & \
            (self.grid['fsh'] == self.fsh) & \
            (self.grid['mlt'] == self.mlt) & \
            (self.grid['sc'] == self.sc) & \
            (self.grid['reimers'] == self.reimers) & \
            (self.grid['blocker'] == self.blocker) & \
            (self.grid['turbulence'] == self.turbulence)

        return self.grid[condition][0]

    def create_progenitor_name(self):
        return f"rgb_m{self.m_i}_" + \
            f"rot{self.rot}_" + \
            f"z{self.z}_" + \
            f"y{self.y}_" + \
            f"fh{self.fh}_" + \
            f"fhe{self.fhe}_" + \
            f"fsh{self.fsh}_" + \
            f"mlt{self.mlt}_" + \
            f"sc{self.sc}_" + \
            f"reimers{self.reimers}_" + \
            f"blocker{self.blocker}_" + \
            f"turbulence{self.turbulence}_" + \
            f"lvl{self.level}_" + \
            f"{self.model_number}.mod"
    

    def calculate_y(self):
        y_primordial = 0.249  # Planck Collaboration (2015)
        y_protosolar = 0.2703  # AGSS09
        z_protosolar = 0.0142  # AGSS09
        # Choi et al. (2016)
        return y_primordial + (y_protosolar - y_primordial) * self.z / z_protosolar

    @classmethod
    def change_grid_file(cls, grid_file):
        cls.grid_file = grid_file


def make_replacements(file_in, file_out, replacements, remove_original=False):
    with open(file_in) as infile, open(file_out, 'w') as outfile:
        for line in infile:
            for src, target in replacements.items():
                line = line.replace(src, target)
            outfile.write(line)
    if remove_original:
        os.remove(file_in)

def create_logdir_name(progenitor, m_env):
        return f"logs_mi{progenitor.m_i}_" + \
            f"menv{m_env}_" + \
            f"rot{progenitor.rot}_" + \
            f"z{progenitor.z}_" + \
            f"y{progenitor.y}_" + \
            f"fh{progenitor.fh}_" + \
            f"fhe{progenitor.fhe}_" + \
            f"fsh{progenitor.fsh}_" + \
            f"mlt{progenitor.mlt}_" + \
            f"sc{progenitor.sc}_" + \
            f"reimers{progenitor.reimers}_" + \
            f"blocker{progenitor.blocker}_" + \
            f"turbulence{progenitor.turbulence}_" + \
            f"lvl{progenitor.level}_" + \
            f"{progenitor.model_number}"

if __name__ == "__main__":

    grid_zip_file = '/home/jomesa/sdb/progenitors/progenitors_20201005.zip'

    grid_name = 'sdb'
    job_description = f'work_{grid_name}'
    template = 'work-r11701'
    progenitors_dir = '../progenitors/'

    #########################################################################################

    m_i_vector = [1.0]
    z_vector = [0.015]
    levels = [-1, 0, 1]

    progenitors = []
    for m_i in m_i_vector:
        for z in z_vector:
            for level in levels:
                progenitors.append(Progenitor(m_i, z, level))

    envelope_mass = np.unique(np.concatenate((
        np.arange(1e-4, 3.1e-3, 1e-4),
        np.arange(4e-3, 1.1e-2, 1e-3))))

    # availiable mixing types:
    # "std" - standard mixing
    # "cpm" - the convective premixing scheme
    # "predictive" - predictive mixing
    mixing = ["cpm"]

    f_he = [0.0]

    #########################################################################################

    for pro in progenitors:
        with ZipFile(grid_zip_file, 'r') as archive:
            models = [os.path.basename(name) for name in archive.namelist()]
            if pro.progenitor_name in models:
                archive.extract(os.path.join(
                    'progenitors', pro.progenitor_name))
        for m_env in envelope_mass:
            log_dir = create_logdir_name(pro, m_env)
            for mix in mixing:
                for f_core in f_he:
                    job_name = f"m{pro.m:.3f}" + \
                        f"_mcore{pro.m_core:.6f}" + \
                        f"_menv{m_env:.5f}" + \
                        f"_z{pro.z:.4f}" + \
                        f"_y{pro.y:.5f}" + \
                        f"_fhe{f_core:.3f}" + \
                        f"_{mix}"
                    print(job_name)
                    dest_dir = f"{job_description}_{job_name}"
                    shutil.copytree(template, dest_dir)
                    shutil.move(os.path.join(dest_dir, "run_make_sdb.sh"),
                                os.path.join(dest_dir, f"r_{grid_name}_{job_name}.sh"))
                    replacements = {
                        "[[MASS]]": f"{pro.m:.3f}",
                        "[[M_HE_CORE]]": f"{pro.m_core:.6f}",
                        "[[Z]]": f"{pro.z:.4f}",
                        "[[Y]]": f"{pro.y:.5f}",
                        "[[MODEL_NAME]]": os.path.join(progenitors_dir, pro.progenitor_name),
                        "[[M_ENV]]": f"{m_env:.5f}",
                        "[[MIXING]]": mix,
                        "[[F_HE]]": f"{f_core:.3f}",
                        "[[LOGDIR]]": log_dir,
                    }
                    make_replacements(os.path.join(dest_dir, 'template_r11701.rb'),
                                      os.path.join(dest_dir, 'make_sdb.rb'),
                                      replacements)
