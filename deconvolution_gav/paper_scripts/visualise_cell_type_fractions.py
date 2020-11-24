#!/usr/bin/env python3

"""
File:         visualise_cell_type_fractions.py
Created:      2020/11/24
Last Changed:
Author:       M.Vochteloo

Copyright (C) 2020 M.Vochteloo
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

A copy of the GNU General Public License can be found in the LICENSE file in the
root directory of this source tree. If not, see <https://www.gnu.org/licenses/>.
"""

# Standard imports.
from __future__ import print_function
from pathlib import Path
import argparse
import os

# Third party imports.
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Local application imports.

# Metadata
__program__ = "Visualise Cell Type Fractions"
__author__ = "Martijn Vochteloo"
__maintainer__ = "Martijn Vochteloo"
__email__ = "m.vochteloo@rug.nl"
__license__ = "GPLv3"
__version__ = 1.0
__description__ = "{} is a program developed and maintained by {}. " \
                  "This program is licensed under the {} license and is " \
                  "provided 'as-is' without any warranty or indemnification " \
                  "of any kind.".format(__program__,
                                        __author__,
                                        __license__)

"""
Syntax:
./visualise_cell_type_fractions.py -cc ../../2020-03-12-deconvolution/partial_deconvolution/ALL_TMM_LOG2/IHC_0CPM_LOG2_FILTERED_CC/deconvolution.txt.gz -sa /groups/umcg-biogen/tmp03/output/2019-11-06-FreezeTwoDotOne/2020-02-03-phenotype-table/2020-09-04.brain.phenotypes.withReannotatedDiagnosis.txt -s rnaseq_id -g predicted.brain.region -d no_predicted_region_available -e pdf
"""


class main():
    def __init__(self):
        # Get the command line arguments.
        arguments = self.create_argument_parser()
        self.cc_path = getattr(arguments, 'cellcount%')
        self.sa_path = getattr(arguments, 'sample_annotation')
        self.sample_id = getattr(arguments, 'sample')
        self.ss_path = getattr(arguments, 'sample_subset')
        self.group_id = getattr(arguments, 'group')
        self.drop = getattr(arguments, 'drop')
        self.extensions = getattr(arguments, 'extension')

        # Set variables.
        self.outdir = os.path.join(str(Path(__file__).parent.parent), 'visualise_cell_type_fractions')
        self.palette = {
            "cortex": "#0072B2",
            "cerebellum": "#D55E00",
            "basalganglia": "#009E73",
            "spinalcord": "#56B4E9",
            "hypothalamus": "#E69F00",
            "hippocampus": "#F0E442",
            "amygdala": "#CC79A7"
        }
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)

        # Set the right pdf font for exporting.
        matplotlib.rcParams['pdf.fonttype'] = 42
        matplotlib.rcParams['ps.fonttype'] = 42

    @staticmethod
    def create_argument_parser():
        parser = argparse.ArgumentParser(prog=__program__,
                                         description=__description__)

        # Add optional arguments.
        parser.add_argument("-v",
                            "--version",
                            action="version",
                            version="{} {}".format(__program__,
                                                   __version__),
                            help="show program's version number and exit")
        parser.add_argument("-cc",
                            "--cellcount%",
                            type=str,
                            required=True,
                            help="The path to the cell count % matrix")
        parser.add_argument("-sa",
                            "--sample_annotation",
                            type=str,
                            required=True,
                            help="The path to the sample annotation matrix")
        parser.add_argument("-s",
                            "--sample",
                            type=str,
                            required=True,
                            help="The column in -sa / --sample_annotation on"
                                 "that matches with the index in -cc / "
                                 "--cellcount%.")
        parser.add_argument("-ss",
                            "--sample_subset",
                            type=str,
                            required=False,
                            default=None,
                            help="A list of samples in -sa / "
                                 "--sample_annotation to include. "
                                 "Default: None.")
        parser.add_argument("-g",
                            "--group",
                            type=str,
                            required=True,
                            help="The column in -sa / --sample_annotation on"
                                 "which to group per row.")
        parser.add_argument("-d",
                            "--drop",
                            nargs="*",
                            type=str,
                            required=False,
                            default=None,
                            help="The values of-g / --group to drop. Default: "
                                 "None. ")
        parser.add_argument("-e",
                            "--extension",
                            nargs="+",
                            type=str,
                            choices=["png", "pdf", "eps"],
                            default=["png"],
                            help="The figure file extension. "
                                 "Default: 'png'.")

        return parser.parse_args()

    def start(self):
        self.print_arguments()

        print("Loading data.")
        cc_df = self.load_file(self.cc_path)
        sa_df = self.load_file(self.sa_path, index_col=None, low_memory=False)

        print("Preprocessing data.")
        cc_df.index.name = self.sample_id
        cc_df.reset_index(drop=False, inplace=True)
        cc_dfm = cc_df.melt(id_vars=[self.sample_id])

        sa_df = sa_df[[self.sample_id, self.group_id]]

        print("Merging data.")
        df = cc_dfm.merge(sa_df, left_on=[self.sample_id], right_on=[self.sample_id])

        print("Filtering data.")
        print("Pre-shape: {}".format(df.shape))
        if self.ss_path is not None:
            ss_df = self.load_file(self.ss_path, index_col=None)
            df = df.loc[~df[self.sample_id].isin(ss_df.iloc[:, 0]), :]
        df = df.loc[~df[self.group_id].isin(self.drop), :]
        print("Post-shape: {}".format(df.shape))

        print("Plotting.")
        print("\tN: {}".format(df.shape[0]))
        print("\tColumn groups: {}".format(df["variable"].unique()))
        print("\tRow groups: {}".format(df[self.group_id].unique()))
        self.plot_distributions(df)

    @staticmethod
    def load_file(path, sep="\t", header=0, index_col=0, nrows=None,
                  low_memory=True):
        df = pd.read_csv(path, sep=sep, header=header, index_col=index_col,
                         nrows=nrows, low_memory=low_memory)
        print("\tLoaded dataframe: {} "
              "with shape: {}".format(os.path.basename(path),
                                      df.shape))
        return df

    def plot_distributions(self, df):
        cell_types = df["variable"].unique()
        groups = df[self.group_id].unique()

        sns.set(rc={'figure.figsize': (20, len(cell_types)*6)})
        sns.set_style("ticks")
        fig, axes = plt.subplots(nrows=len(cell_types), ncols=3,
                                 gridspec_kw={'width_ratios': [0.45, 0.45, 0.05]})

        for i, ct in enumerate(cell_types):
            subset = df.loc[df["variable"] == ct, :]

            ax1, ax2, ax3 = axes[i, :]

            # AX1
            sns.despine(fig=fig, ax=ax1)
            handles = []
            for group in groups:
                data = subset.loc[subset[self.group_id] == group, "value"].copy()
                data.name = group
                sns.kdeplot(data, shade=True, alpha=0.3, ax=ax1, color=self.palette[group],
                            legend=False)
                handles.append(mpatches.Patch(color=self.palette[group], alpha=0.3, label="{} [n={}]".format(group, len(data))))

            xlabel = ""
            if ct == cell_types[-1]:
                xlabel = "predicted cell proportion"
            self.set_text(ax1, ct, subset.shape[0], xlabel, "frequency")

            # AX2
            sns.despine(fig=fig, ax=ax2)
            ax2.axhline(subset["value"].mean(), ls='--', color="#000000", zorder=-1)
            sns.boxplot(x=self.group_id, y="value", data=subset,
                        palette=self.palette,
                        boxprops=dict(alpha=.3),
                        zorder=1,
                        ax=ax2)
            xlabels = ["" for _ in ax2.get_xticklabels()]
            if ct == cell_types[-1]:
                xlabels = ax2.get_xticklabels()
            ax2.set_xticklabels(xlabels, rotation=65, horizontalalignment='right')
            self.set_text(ax2, ct, subset.shape[0], "", "predicted cell proportion")

            # AX3
            ax3.axis('off')
            if i == 0:
                ax3.legend(handles=handles, loc="upper right")

        plt.tight_layout()
        for extension in self.extensions:
            fig.savefig(os.path.join(self.outdir, "cell_fraction_distribution_{}.{}".format(self.group_id, extension)))
        plt.close()

    @staticmethod
    def set_text(ax, ct, n, xlabel, ylabel):
        ax.set_xlabel(xlabel,
                      fontsize=10,
                      fontweight='bold')
        ax.set_ylabel(ylabel,
                      fontsize=10,
                      fontweight='bold')
        ax.text(0.5, 1, ct,
                fontsize=14, weight='bold', ha='center', va='bottom',
                transform=ax.transAxes)

    def print_arguments(self):
        print("Arguments:")
        print("  > Cell count % path: {}".format(self.cc_path))
        print("  > Sample annotation path: {}".format(self.sa_path))
        print("  > Sample ID: {}".format(self.sample_id))
        print("  > Sample subset path: {}".format(self.ss_path))
        print("  > Group ID: {}".format(self.group_id))
        print("  > Group drop: {}".format(self.drop))
        print("  > Extension: {}".format(self.extensions))
        print("  > Output directory: {}".format(self.outdir))
        print("")


if __name__ == '__main__':
    m = main()
    m.start()
