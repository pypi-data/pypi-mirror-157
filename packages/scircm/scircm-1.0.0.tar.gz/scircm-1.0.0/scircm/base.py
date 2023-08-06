###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

import numpy as np
import pandas as pd
import os
import json
from scivae import VAE
import seaborn as sns
from sciutil import SciUtil, SciException
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sciviso import Heatmap
from matplotlib_venn import venn3
import matplotlib
from matplotlib import rcParams
from tensorflow import keras


class SciRCMException(SciException):
    def __init__(self, message=''):
        Exception.__init__(self, message)


class SciRCM:

    def __init__(self, meth_file: str, rna_file: str, proteomics_file: str,
                 rna_logfc: str, rna_padj: str,
                 meth_diff: str, meth_padj: str,
                 prot_logfc: str, prot_padj: str,
                 gene_id: str,
                 rna_padj_cutoff=0.05, prot_padj_cutoff=0.05, meth_padj_cutoff=0.05,
                 rna_logfc_cutoff=1.0, prot_logfc_cutoff=0.5, meth_diff_cutoff=10, output_dir='.',
                 output_filename=None, non_coding_genes=None, debug_on=False, sep=',',
                 bg_type='P|(M&R)', sciutil=None, colours=None, logfile=None):
        self.u = SciUtil() if sciutil is None else sciutil
        plt.rcParams['svg.fonttype'] = 'none'
        self.meth_df = pd.read_csv(meth_file, sep=sep)
        self.rna_df = pd.read_csv(rna_file, sep=sep)
        self.prot_df = pd.read_csv(proteomics_file, sep=sep)
        self.meth_diff = meth_diff
        self.merged_df = None
        self.prot_logfc = prot_logfc
        self.rna_logfc = rna_logfc
        self.rna_padj = rna_padj
        self.meth_padj = meth_padj
        self.prot_padj = prot_padj
        self.gene_id = gene_id
        self.logfile = open(logfile, "w+") if logfile is not None else None  # File for logging results
        self.rna_padj_cutoff, self.meth_padj_cutoff, self.prot_padj_cutoff = rna_padj_cutoff, meth_padj_cutoff, prot_padj_cutoff
        self.rna_logfc_cutoff, self.meth_diff_cutoff, self.prot_logfc_cutoff = rna_logfc_cutoff, meth_diff_cutoff, prot_logfc_cutoff
        self.debug = debug_on
        self.output_dir = output_dir
        self.bg_type = bg_type
        self.bg_list = ['(P&M)|(P&R)', '(P&M)|(P&R)|(M&R)', '*', 'P&M&R', 'P|M|R', 'P|(M&R)']
        if bg_type not in self.bg_list:
            self.u.err_p(['ERROR: selected background type was not allowed, please choose from one of: ', self.bg_list,
                          '\n Note: | means OR and & means AND'])
        self.output_filename = output_filename if output_filename else f'scircm_r{rna_logfc_cutoff}-{rna_padj_cutoff}' \
                                                                       f'_p{prot_logfc_cutoff}-{prot_padj_cutoff}' \
                                                                       f'_m{meth_diff_cutoff}-{meth_padj_cutoff}.csv'

        self.non_coding_genes = non_coding_genes
        self.colours = colours if colours else ['#483873', '#1BD8A6', '#B117B7', '#AAC7E2', '#FFC107', '#016957', '#9785C0',
             '#D09139', '#338A03', '#FF69A1', '#5930B1', '#FFE884', '#35B567', '#1E88E5',
             '#ACAD60', '#A2FFB4', '#B618F5', '#854A9C']
        colour_map = {'MDE': '#6aaf44', 'MDE_TMDS': '#0e8e6d', 'MDE_ncRNA': '#9edb77',
                      'MDS': '#d8419b', 'MDS_TMDE': '#e585c0', 'MDS_ncRNA': '#d880b4',
                      'TPDE': '#e68e25', 'TPDE_TMDS': '#844c0f',
                      'TPDS': '#603c99', 'TPDS_TMDE': '#9b29b7',
                      'TMDE': '#fe2323', 'TMDS': '#0101d7'}
        prot_c = '#0101d7'
        rna_c = '#e68e25'
        meth_c = '#6aaf44'
        # Contains genes for the non-coding region (use for human only).
        self.df = None
        # Contains the vae data
        self.vae = None

    def run(self, fill_protein=False, protein_cols=None):
        # Merge the dataframes together
        self.merge_dfs(fill_protein, protein_cols)
        # Generate background
        self.df = self.gen_bg()
        # Calculate groups
        grps, grp_labels = self.run_rcm()
        # Save the DF and return the groupings
        self.df.to_csv(os.path.join(self.output_dir, self.output_filename), index=False)
        return grps, grp_labels

    @staticmethod
    def _get_bg_filter(bg_type, prot_val, rna_val, meth_val, prot_padj_cutoff, meth_padj_cutoff, rna_padj_cutoff):
        c = 0
        if bg_type == 'P|(M&R)':  # Protein AND (DNA methylation OR RNA)
            c = 1 if prot_val <= prot_padj_cutoff else 0
            c += 1 if rna_val <= rna_padj_cutoff and meth_val <= meth_padj_cutoff else 0
        elif bg_type == 'P|M|R':  # Protein OR methylation OR RNA
            c = 1 if prot_val <= prot_padj_cutoff else 0
            c += 1 if rna_val <= rna_padj_cutoff else 0
            c += 1 if meth_val <= meth_padj_cutoff else 0
        elif bg_type == 'P&M&R':  # Protein AND Methylation AND RNA
            c = 1 if (prot_val <= prot_padj_cutoff and rna_val <= rna_padj_cutoff and meth_val <= meth_padj_cutoff) else 0
        elif bg_type == '(P&M)|(P&R)|(M&R)':  # At least two are significant
            c = 1 if (prot_val <= prot_padj_cutoff and rna_val <= rna_padj_cutoff) else 0
            c += 1 if (prot_val <= prot_padj_cutoff and meth_val <= meth_padj_cutoff) else 0
            c += 1 if (rna_val <= rna_padj_cutoff and meth_val <= meth_padj_cutoff) else 0
        elif bg_type == '(P&M)|(P&R)':  # Protein and one other
            c = 1 if (prot_val <= prot_padj_cutoff and rna_val <= rna_padj_cutoff) else 0
            c += 1 if (prot_val <= prot_padj_cutoff and meth_val <= meth_padj_cutoff) else 0
        elif bg_type == '*':  # Use all genes as the background
            c = 1
        return c

    def gen_bg(self, bg_type=None, prot_padj_cutoff=None, rna_padj_cutoff=None, meth_padj_cutoff=None):
        """
        Generate a background dataset i.e. since the RCM requires at least two of the 3 datasets to
        have a p value beneath a threshold we reduce our dataset to be smaller.
        """
        bg_type = bg_type if bg_type else self.bg_type
        prot_padj_cutoff = prot_padj_cutoff if prot_padj_cutoff else self.prot_padj_cutoff
        meth_padj_cutoff = meth_padj_cutoff if meth_padj_cutoff else self.meth_padj_cutoff
        rna_padj_cutoff = rna_padj_cutoff if rna_padj_cutoff else self.rna_padj_cutoff
        filter_vals = np.zeros(len(self.merged_df))
        meth_padj_values = self.merged_df[self.meth_padj].values
        prot_padj_values = self.merged_df[self.prot_padj].values

        # Choose the background dataframe
        for i, rna_padj in enumerate(self.merged_df[self.rna_padj].values):
            c = self._get_bg_filter(bg_type, prot_padj_values[i], rna_padj, meth_padj_values[i],
                                    prot_padj_cutoff, meth_padj_cutoff, rna_padj_cutoff)
            filter_vals[i] = c

        df = self.merged_df.copy()
        # Filter the df to become the background df
        df['Number of significant datasets'] = filter_vals
        # Filter DF to only include those that are sig in two.
        df = df[df['Number of significant datasets'] >= 1]
        df = df.reset_index()  # Reset the index of the dataframe

        return df

    def merge_dfs(self, fill_protein=False, protein_cols=None):
        self.rna_df = self.rna_df.set_index(self.gene_id)
        self.df = self.rna_df.merge(self.meth_df, on=self.gene_id, how='outer', suffixes=['_r', '_m'])
        self.df = self.df.merge(self.prot_df, on=self.gene_id, how='outer', suffixes=['', '_p'])
        # Fill any of the values with NAs (p values need to be filled with 1's)
        self.df[[self.meth_padj]] = self.df[[self.meth_padj]].fillna(value=1.0)
        self.df[[self.rna_padj]] = self.df[[self.rna_padj]].fillna(value=1.0)
        self.df[[self.prot_padj]] = self.df[[self.prot_padj]].fillna(value=1.0)
        # Fill the rest of the values with 0's
        if fill_protein and protein_cols is not None:
            # Here we may want to impute the protein values ToDo: implement more than None
            for c in protein_cols:
                if c not in self.df.columns:
                    self.u.err_p(["Unable to impute for column: ", c, "as it wasn't in the DF. Please check this col "
                                                                      "exists. \nContinuing..."])
                else:
                    gr0_vals = self.df[c].values.copy()[np.where(self.df[c].values > 0)[0]]
                    self.df[c] = self.df[c].fillna(min(gr0_vals))
        self.df = self.df.fillna(0)
        self.df.to_csv(os.path.join(self.output_dir, "merged_df.csv"), index=False)
        self.merged_df = self.df.copy()

    def run_rcm(self):
        lbls = ['None'] * len(self.df)
        self.df['RegulatoryLabels'] = lbls
        if self.logfile is not None:
            self.logfile.write(f'MethylationState,RNAseqState,ProteinState,Label,NumGenes\n')
        grp1 = self.get_grp(meth_c='pos', rna_c='neg', prot_c='neg', grp_id='MDS')
        grp2 = self.get_grp(meth_c='pos', rna_c='pos', prot_c='neg', grp_id='TPDE_TMDS')
        grp3 = self.get_grp(meth_c='pos', rna_c='pos', prot_c='pos', grp_id='TPDE')
        grp4 = self.get_grp(meth_c='pos', rna_c='neg', prot_c='pos', grp_id='TMDE')
        grp5 = self.get_grp(meth_c='neg', rna_c='neg', prot_c='neg', grp_id='TPDS')
        grp6 = self.get_grp(meth_c='neg', rna_c='pos', prot_c='neg', grp_id='TMDS')
        grp7 = self.get_grp(meth_c='neg', rna_c='pos', prot_c='pos', grp_id='MDE')
        grp8 = self.get_grp(meth_c='neg', rna_c='neg', prot_c='pos', grp_id='TPDS_TMDE')

        grp9 = self.get_grp(meth_c='-', rna_c='neg', prot_c='pos', grp_id='TPDS_TMDE')
        grp10 = self.get_grp(meth_c='-', rna_c='pos', prot_c='neg', grp_id='TPDE_TMDS')
        grp11 = self.get_grp(meth_c='-', rna_c='neg', prot_c='neg', grp_id='TPDS')
        grp12 = self.get_grp(meth_c='-', rna_c='pos', prot_c='pos', grp_id='TPDE')

        grp13 = self.get_grp(meth_c='pos', rna_c='-', prot_c='pos', grp_id='TMDE')
        grp14 = self.get_grp(meth_c='pos', rna_c='-', prot_c='neg', grp_id='TMDS')
        grp15 = self.get_grp(meth_c='neg', rna_c='-', prot_c='pos', grp_id='TMDE')
        grp16 = self.get_grp(meth_c='neg', rna_c='-', prot_c='neg', grp_id='TMDS')

        grp17 = self.get_grp(meth_c='pos', rna_c='pos', prot_c='-', grp_id='TPDE_TMDS')
        grp18 = self.get_grp(meth_c='pos', rna_c='neg', prot_c='-', grp_id='MDS_TMDE')
        grp19 = self.get_grp(meth_c='neg', rna_c='pos', prot_c='-', grp_id='MDE_TMDS')
        grp20 = self.get_grp(meth_c='neg', rna_c='neg', prot_c='-', grp_id='TPDS_TMDE')

        # Here we want to add Methylation driven genes
        if self.non_coding_genes:
            grp21 = self.get_grp(meth_c='pos', rna_c='-', prot_c='-', grp_id='MDS-ncRNA', filter_list=self.non_coding_genes)
            grp22 = self.get_grp(meth_c='neg', rna_c='-', prot_c='-', grp_id='MDE-ncRNA', filter_list=self.non_coding_genes)
        else:
            grp21 = []
            grp22 = []

        grp23 = self.get_grp(meth_c='-', rna_c='-', prot_c='neg', grp_id='TMDS')
        grp24 = self.get_grp(meth_c='-', rna_c='-', prot_c='pos', grp_id='TMDE')

        grp_labels = ['MDS',
                     'TPDS',
                     'MDE_TMDS',
                     'MDS_TMDE',
                     'TPDE_TMDS',
                     'TPDE',
                     'TPDS_TMDE',
                     'MDE',
                     'TMDE',
                     'TMDS'
                     ]
        grps = [list(grp1) + list(grp21),
                list(grp5) + list(grp11),
                grp19,
                grp18,
                list(grp17) + list(grp10) + list(grp2),
                list(grp12) + list(grp3),
                list(grp20) + list(grp8) + list(grp9),
                list(grp7) + list(grp22),
                list(grp13) + list(grp15) + list(grp4) + list(grp24),
                list(grp6) + list(grp14) + list(grp16) + list(grp23)]
        # Close the logfile
        if self.logfile is not None:
            self.logfile.close()
        return grps, grp_labels

    def get_df(self):
        return self.df

    def get_grp(self, meth_c, rna_c, prot_c, grp_id, filter_list=None):
        """ Get a single group """
        meth_change = self.df[self.meth_diff].values
        rna_change = self.df[self.rna_logfc].values
        prot_change = self.df[self.prot_logfc].values

        meth_padj = self.df[self.meth_padj].values
        rna_padj = self.df[self.rna_padj].values
        prot_padj = self.df[self.prot_padj].values

        grp = np.ones(len(meth_change))
        if rna_c == 'pos':
            grp *= 1.0 * (rna_change >= self.rna_logfc_cutoff) * (rna_padj <= self.rna_padj_cutoff)
        elif rna_c == 'neg':
            grp *= 1.0 * (rna_change <= (-1 * self.rna_logfc_cutoff)) * (rna_padj <= self.rna_padj_cutoff)
        else:
            # i.e. this gene should belong in the group if it fails to get assigned to the others i.e.
            # misses out based on the pvalue OR the logFC (hence the plus)
            grp *= (1.0 * (rna_padj > self.rna_padj_cutoff) + (1.0 * (abs(rna_change) < self.rna_logfc_cutoff)))

        if prot_c == 'pos':
            grp *= 1.0 * (prot_change >= self.prot_logfc_cutoff) * (1 * prot_padj <= self.prot_padj_cutoff)
        elif prot_c == 'neg':
            grp *= 1.0 * (prot_change <= (-1 * self.prot_logfc_cutoff)) * (1 * prot_padj <= self.prot_padj_cutoff)
        else:
            grp *= 1.0 * (1.0 * prot_padj > self.prot_padj_cutoff) + (abs(prot_change) < self.prot_logfc_cutoff)

        if meth_c == 'pos':
            grp *= 1.0 * (meth_change >= self.meth_diff_cutoff) * (meth_padj <= self.meth_padj_cutoff)
        elif meth_c == 'neg':
            grp *= 1.0 * (meth_change <= (-1 * self.meth_diff_cutoff)) * (meth_padj <= self.meth_padj_cutoff)
        else:
            grp *= 1.0 * ((1.0 * meth_padj > self.meth_padj_cutoff) + (abs(meth_change) < self.meth_diff_cutoff))

        # If we have a filter list of genes, then the genes MUST also be within this list
        genes_in_list = []
        if filter_list:
            for g in self.df[self.gene_id].values:
                if g in filter_list:
                    genes_in_list.append(1)
                else:
                    genes_in_list.append(0)
            grp *= np.array(genes_in_list)

        # Keep only the genes in this group
        grp_genes = self.df[self.gene_id].values[np.where(grp > 0)[0]]

        if self.debug:
            self.u.dp([grp_id, f'{meth_c} METH', f'{rna_c} RNA', f'{prot_c} PROT',
                  len(list(grp)), '\n', ', '.join(list(grp_genes))])
        if self.logfile is not None:
            # Print to logfile the results
            self.logfile.write(f'{meth_c},{rna_c},{prot_c},{grp_id},{len(list(grp_genes))}\n')
        # Add in the labels
        grp_ids = np.where(grp > 0)[0]
        grp_labels = list(self.df['RegulatoryLabels'].values)
        for i, g in enumerate(self.df[self.gene_id].values):
            if g in grp_genes:
                if grp_labels[i] and grp_labels[i] != 'None':
                    self.u.warn_p(["Possible duplicate:", grp_labels[i], grp_id, g])
                    print(self.df[self.df[self.gene_id] == g])
                grp_labels[i] = grp_id

        self.df['RegulatoryLabels'] = grp_labels
        return self.df[self.gene_id][grp_ids]

    def save_df(self, output_filename):
        self.df.to_csv(output_filename, index=False)

    def get_genes_in_reg_grp(self, label, gene_label=None):
        gene_label = self.gene_id if not gene_label else gene_label
        return list(set(self.df[self.df["RegulatoryLabels"] == label][gene_label].values))

    def get_all_assigned_genes(self, gene_label=None):
        gene_label = self.gene_id if not gene_label else gene_label
        return list(set(self.df[self.df["RegulatoryLabels"] != 'None'][gene_label].values))

    def get_all_unassigned_genes(self, gene_label=None):
        gene_label = self.gene_id if not gene_label else gene_label
        return list(set(self.df[self.df["RegulatoryLabels"] == 'None'][gene_label].values))

    def save_vae(self, weight_file_path='model_weights.h5',
                      optimizer_file_path='model_optimiser.pkl', config_json='config.json'):
        # Save the VAE to a hd5 file
        self.vae.save(weight_file_path, optimizer_file_path, config_json)

    def add_vae_values_to_df(self, vae_df: pd.DataFrame, gene_id: str, data_cols=None, output_filename=None):
        data_cols = data_cols if data_cols is not None else [c for c in vae_df.columns if c != gene_id]
        vae_input_values = vae_df[data_cols].values
        scaler = MinMaxScaler(copy=True)
        scaled_vals = scaler.fit_transform(vae_input_values)
        vae_data = self.vae.encode_new_data(scaled_vals, encoding_type="z")
        for i in range(0, len(vae_data[0])):
            vae_df[f'VAE{i}'] = vae_data[:, i]
        if output_filename is not None:
            vae_df.to_csv(output_filename, index=False)
        return vae_df

    def compute_vae(self, vae_df: pd.DataFrame, gene_id_col: str, json_config_file: str,
                    save_vae=False, load_presaved=False, weight_file_path='model_weights.h5',
                    optimizer_file_path='model_optimiser.pkl', config_json='config.json'):
        """ Use a VAE to compress a dataset. Dataset must be only numeric. """
        with open(json_config_file, "r") as fp:
            config = json.load(fp)
            data_cols = [c for c in vae_df.columns if c != gene_id_col]
            dataset = vae_df[data_cols].values
            vae = VAE(dataset, dataset, ["None"] * len(dataset), config, f'vae_rcm')
            # Load a pre-saved model
            if load_presaved:
                vae.load(weight_file_path, optimizer_file_path, config_json)
            else:
                vae.encode('default', epochs=config['epochs'], batch_size=config['batch_size'])
            self.vae = vae
            if save_vae:
                self.save_vae(weight_file_path, optimizer_file_path, config_json)

    def rank_rcm_by_vae(self, vae_df: pd.DataFrame, cluster_name: str, vae_node: int, gene_id: str):
        """ Dataset must include the numeric values and the gene ID. vae_node starts at 0. """
        # Now we want to rank a cluster by a specific VAE node
        # First we need to encode the values for the genes associated with that cluster
        genes_in_cluster = self.df[self.df['RegulatoryLabels'] == cluster_name][self.gene_id].values
        # Print out an error message if there are no genes in this cluster
        if len(genes_in_cluster) < 1:
            self.u.err_p(["ERROR: Rank RCM by VAE. Seems as though you made an error as there are no genes"
                          " in this cluster. Likely causes are: 1) no genes were assigned to this cluster, 2) you"
                          " haven't run the RCM yet (run rcm.run()) 3) you got the cluster name wrong: ", cluster_name])
            return
        # Otherwise let's get the matching data from their dataset
        genes_idxs = []
        for i, g in enumerate(vae_df[gene_id].values):
            if g in genes_in_cluster:
                genes_idxs.append(i)
        data_cols = [c for c in vae_df.columns if c != gene_id]
        gene_names = vae_df[gene_id].values[genes_idxs]
        vae_input_values = vae_df[data_cols].values[genes_idxs]
        scaler = MinMaxScaler(copy=True)
        scaled_vals = scaler.fit_transform(vae_input_values)
        vae_data = self.vae.encode_new_data(scaled_vals, encoding_type="z")
        # Now we want to return the list of genes ranked by the node of interest
        idxs_sorted = (-vae_data[:, vae_node]).argsort()
        sorted_df = pd.DataFrame()
        sorted_df[gene_id] = gene_names[idxs_sorted]
        sorted_df[f'node_{vae_node}'] = vae_data[:, vae_node][idxs_sorted]
        return sorted_df

    def load_model(self, path_to_hdf_model, vae_df, gene_id_col, json_config_file):
        with open(json_config_file, "r") as fp:
            config = json.load(fp)
            data_cols = [c for c in vae_df.columns if c != gene_id_col]
            dataset = vae_df[data_cols].values
            self.vae = VAE(dataset, dataset, ["None"] * len(dataset), config, f'vae_rcm')
            self.vae.vae = keras.models.load_model(path_to_hdf_model)

    """ 
    Plotting (perhaps modularise)
    """
    def plot_venn(self, output_dir="", title="RNA Protein & DNA Meth overlap", fig_type='svg', show_plt=False):
        fig, ax = plt.subplots()
        sns.set_style('white')
        sns.color_palette('RdBu_r')
        font = {'family': 'normal',
                'size': 8}
        matplotlib.rc('font', **font)
        rcParams['figure.figsize'] = 6, 6
        prot_genes = self.df[self.gene_id].values[np.where(self.df[self.prot_padj].values < self.prot_padj_cutoff)[0]]
        meth_genes = self.df[self.gene_id].values[np.where(self.df[self.meth_padj].values < self.meth_padj_cutoff)[0]]
        rna_genes = self.df[self.gene_id].values[np.where(self.df[self.rna_padj].values < self.rna_padj_cutoff)[0]]

        venn3([set(prot_genes), set(rna_genes), set(meth_genes)], set_labels=['Proteomics', 'RNAseq',
                                                                              'DNA Methylation'],
              set_colors=('r', 'g', 'b'),)
        plt.title(title)
        plt.savefig(os.path.join(output_dir, f'Venn3{title.replace(" ", "")}.{fig_type}'))
        if show_plt:
            plt.show()

    def plot_values_by_rank(self, vis_df_filename, cols, gene_id, rcm_col="RegulatoryLabels", num_values=10,
                                show_plt=False, cluster_rows=False, cluster_cols=False, title='', num_nodes=3,
                            meth_min=-100, meth_max=100, rna_min=-4, rna_max=4, prot_min=-2, prot_max=2, output_dir=""):
        rcm_grps = ["MDS", "TPDE_TMDS", "TPDE", "TMDE", "TPDS_TMDE", "TPDS", "TMDS", "MDE", "MDE_TMDS",
                    "MDE-ncRNA", "MDS-ncRNA"]
        vae_cols = [f'VAE{i}' for i in range(0, num_nodes)]
        vis_df = pd.read_csv(vis_df_filename)
        print(vis_df.head())
        meth_min = np.min(vis_df[self.meth_diff])
        meth_max = np.max(vis_df[self.meth_diff])
        rna_min = np.min(vis_df[self.rna_logfc])
        rna_max = np.max(vis_df[self.rna_logfc])
        prot_min = np.min(vis_df[self.prot_logfc])
        prot_max = np.max(vis_df[self.prot_logfc])
        # Keep things symmetrical
        if abs(prot_min) > prot_max:
            prot_max = abs(prot_min)
        else:
            prot_min = -1 * prot_max
        if abs(rna_min) > rna_max:
            rna_max = abs(rna_min)
        else:
            rna_min = -1 * rna_max
        if abs(meth_min) > meth_max:
            meth_max = abs(meth_min)
        else:
            meth_min = -1 * meth_max
        for rcm_grp in rcm_grps:
            print(rcm_grp)
            sns.set_style("ticks")
            rcm_df = vis_df[vis_df[rcm_col] == rcm_grp]
            if len(rcm_df) > 0:
                for r_i, r_c in enumerate(cols):
                    # First add the bottom ones
                    fig, axes = plt.subplots(ncols=3, figsize=(3, 2))
                    rcm_df_sorted = rcm_df.sort_values(by=[r_c])
                    rcm_df_largest = rcm_df_sorted.nlargest(num_values, r_c)
                    rcm_df_tails = rcm_df_largest.append(rcm_df_sorted.nsmallest(num_values, r_c))  # Add the smallest and the largest
                    ax1, ax2, ax3 = axes
                    m_df = pd.DataFrame()
                    m_df['Gene'] = rcm_df_tails[gene_id].values
                    m_df['M. diff'] = rcm_df_tails[self.meth_diff].values
                    m_df['RNA logFC'] = rcm_df_tails[self.rna_logfc].values
                    m_df['Prot logFC'] = rcm_df_tails[self.prot_logfc].values

                    hm = Heatmap(m_df, ['M. diff'], 'Gene', cluster_cols=False, cluster_rows=False) #, vmin=meth_min, vmax=meth_max)
                    ax1 = hm.plot_hm(ax1)
                    ax1.set_xticklabels([])
                    ax1.title.set_text('M. diff')
                    ax1.tick_params(axis=u'x', which=u'both', length=0)

                    hm = Heatmap(m_df, ['RNA logFC'], 'Gene',  cluster_cols=False, cluster_rows=False)
                    ax2 = hm.plot_hm(ax2)
                    ax2.title.set_text('RNA logFC')
                    ax2.set_yticklabels([])
                    ax2.set_xticklabels([])
                    ax2.tick_params(axis=u'both', which=u'both', length=0)

                    hm = Heatmap(m_df, ['Prot logFC'], 'Gene',  cluster_cols=False, cluster_rows=False)
                    ax3 = hm.plot_hm(ax3)
                    ax3.title.set_text('Prot. logFC')
                    ax3.set_yticklabels([])
                    ax3.set_xticklabels([])
                    ax3.tick_params(axis=u'both', which=u'both', length=0)

                    #fig.colorbar(im1, ax=ax1, shrink=0.3, aspect=3, orientation='horizontal')

                    plt.savefig(f'{output_dir}{title.replace(" ", "_")}_{rcm_grp}_{r_c}.pdf')
                    if show_plt:
                        plt.show()
            else:
                self.u.dp(["No values in grp: ", rcm_grp])
